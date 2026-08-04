async function refreshAdminUI() {
  if (window.location.pathname.endsWith('admin.html') && typeof renderAdminStandalonePage === 'function') {
    await renderAdminStandalonePage();
  } else if (typeof openAdminPanelModal === 'function') {
    await refreshAdminUI();
  }
}
/* ==========================================================================
   GLOBAL CONSTANTS & CONFIGURATION
   ========================================================================== */
const ADMIN_PASS = 'chinhanxt';
const VIP_KEYS_STORAGE = 'lms_vip_keys_db';
const USERS_DB_STORAGE = 'lms_users_db';
const DEVICE_ID_KEY = 'lms_device_fingerprint';
const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';
const CLOUD_DB_ENDPOINT = 'https://jsonblob.com/api/jsonBlob/019fcb1f-708b-750f-948f-caa9398416e8';

// Save & Overwrite Cloud DB Directly for Delete & Modify Actions
async function saveAndPushCloudData(keys, users) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));

  try {
    const putRes = await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keys: keys,
        users: users
      })
    });

    if (putRes.ok) {
      await putRes.json();
      console.log('Cloud DB save confirmed.');
    }
  } catch (e) {
    console.warn('Cloud DB save error:', e);
  }
}




function aggregateUsersFromKeys(keys, users) {
  const mergedUsers = [...users];

  // 1. Sync used keys to users
  for (const k of keys) {
    if (k.status === 'used' && k.deviceId) {
      let uObj = mergedUsers.find(u => u.deviceId === k.deviceId);
      if (uObj) {
        uObj.role = 'vip';
        uObj.activatedKey = k.key;
      }
    }
  }

  // 2. Sync user key activations to keys array
  for (const u of mergedUsers) {
    if (u.role === 'vip' && u.activatedKey && u.activatedKey.startsWith('MAC-')) {
      let kObj = keys.find(k => k.key.toUpperCase() === u.activatedKey.toUpperCase());
      if (kObj) {
        kObj.status = 'used';
        kObj.deviceId = u.deviceId;
      }
    }
  }

  return mergedUsers;
}

// Fetch Both Keys & Users from Cloud DB & Merge Cleanly
async function fetchCloudData() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store', signal: controller.signal });
    clearTimeout(timer);

    if (res.ok) {
      const json = await res.json();
      if (json) {
        const dbObj = json.data || json;
        const cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        const cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];

        // Merge Keys
        const localKeysData = localStorage.getItem(VIP_KEYS_STORAGE);
        let localKeys = localKeysData ? JSON.parse(localKeysData) : [];
        const mergedKeys = [...cloudKeys];
        for (const lk of localKeys) {
          if (!mergedKeys.some(ck => ck.key.toUpperCase() === lk.key.toUpperCase())) {
            mergedKeys.push(lk);
          }
        }

        // Merge Users
        const localUsersData = localStorage.getItem(USERS_DB_STORAGE);
        let localUsers = localUsersData ? JSON.parse(localUsersData) : [];
        let mergedUsers = [...cloudUsers];
        for (const lu of localUsers) {
          const idx = mergedUsers.findIndex(cu => cu.deviceId === lu.deviceId);
          if (idx >= 0) {
            mergedUsers[idx] = lu;
          } else {
            mergedUsers.push(lu);
          }
        }

        // Auto-aggregate
        mergedUsers = aggregateUsersFromKeys(mergedKeys, mergedUsers);

        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
        localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

        return { keys: mergedKeys, users: mergedUsers };
      }
    }
  } catch (e) {
    console.warn('Cloud DB fetch offline/timeout, using local storage.', e);
  }

  const lKeys = getVipKeysDB();
  const lUsers = aggregateUsersFromKeys(lKeys, getUsersDB());
  return { keys: lKeys, users: lUsers };
}

// Push Both Keys & Users to Cloud DB Safely with Merge
async function pushCloudData(keysToPush, usersToPush) {
  try {
    const getRes = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store' });
    let cloudKeys = [];
    let cloudUsers = [];
    if (getRes.ok) {
      const json = await getRes.json();
      if (json) {
        const dbObj = json.data || json;
        cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];
      }
    }

    const mergedKeys = [...cloudKeys];
    for (const k of (keysToPush || getVipKeysDB())) {
      const idx = mergedKeys.findIndex(ck => ck.key.toUpperCase() === k.key.toUpperCase());
      if (idx >= 0) mergedKeys[idx] = k; else mergedKeys.push(k);
    }

    let mergedUsers = [...cloudUsers];
    for (const u of (usersToPush || getUsersDB())) {
      const idx = mergedUsers.findIndex(cu => cu.deviceId === u.deviceId);
      if (idx >= 0) mergedUsers[idx] = u; else mergedUsers.push(u);
    }

    // Auto-aggregate
    mergedUsers = aggregateUsersFromKeys(mergedKeys, mergedUsers);

    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
    localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

    const putRes = await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'LMS_VIP_KEYS',
        data: { keys: mergedKeys, users: mergedUsers }
      })
    });

    if (putRes.ok) {
      await putRes.json();
    }
  } catch (e) {
    console.warn('Failed to push to Cloud DB:', e);
  }
}

/* ==========================================================================
   ADMIN PANEL & USER MANAGEMENT SYSTEM (Pass: chinhanxt)
   ========================================================================== */







// Generate or retrieve unique device fingerprint
function getDeviceId() {
  let devId = localStorage.getItem(DEVICE_ID_KEY);
  if (!devId) {
    const randomStr = Math.random().toString(36).substring(2, 8).toUpperCase();
    const platform = (navigator.platform || 'DEV').replace(/[^a-zA-Z0-9]/g, '').substring(0, 4).toUpperCase();
    devId = `${platform}-${randomStr}`;
    localStorage.setItem(DEVICE_ID_KEY, devId);
  }
  return devId;
}

// Track/Register user access in Users DB
async function trackCurrentDeviceUser() {
  const devId = getDeviceId();
  const role = getUserRole() || 'guest';
  const activatedKey = localStorage.getItem(ACTIVATED_KEY_STORAGE) || 'N/A';
  const userAgent = navigator.userAgent.includes('Mobile') ? '📱 Điện thoại' : '💻 Máy tính';
  const lastActive = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');

  let users = getUsersDB();
  let user = users.find(u => u.deviceId === devId);

  if (user) {
    user.role = role;
    user.activatedKey = activatedKey;
    user.lastActive = lastActive;
    user.deviceType = userAgent;
  } else {
    users.push({
      deviceId: devId,
      name: `Học viên ${devId}`,
      role: role,
      activatedKey: activatedKey,
      deviceType: userAgent,
      createdAt: lastActive,
      lastActive: lastActive
    });
  }

  pushCloudKeysDB(getVipKeysDB());
}

function getUsersDB() {
  const data = localStorage.getItem(USERS_DB_STORAGE);
  if (!data) {
    const currentDevId = getDeviceId();
    const initUsers = [
      {
        deviceId: currentDevId,
        name: `Học viên (Máy này)`,
        role: getUserRole() || 'guest',
        activatedKey: localStorage.getItem(ACTIVATED_KEY_STORAGE) || 'N/A',
        deviceType: navigator.userAgent.includes('Mobile') ? '📱 Điện thoại' : '💻 Máy tính',
        createdAt: new Date().toLocaleDateString('vi-VN'),
        lastActive: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN')
      }
    ];
    localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(initUsers));
    return initUsers;
  }
  return JSON.parse(data);
}

function saveUsersDB(users) {
  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));
}

// Keys DB
function getVipKeysDB() {
  const data = localStorage.getItem(VIP_KEYS_STORAGE);
  if (!data) {
    const initialKeys = [
     
      
    ];
    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(initialKeys));
    return initialKeys;
  }
  return JSON.parse(data);
}

function saveVipKeysDB(keys) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
}

async function generateNewVipKey() {
  const code = 'MAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
  let keys = await fetchCloudKeysDB();
  keys.push({
    key: code,
    status: 'unused',
    deviceId: null,
    createdAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN')
  });
  await pushCloudKeysDB(keys);
  return code;
}

async function redeemVipKeyAsync(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();
  let cloudData = await fetchCloudData();
  let keys = cloudData.keys;
  let users = cloudData.users;
  const currentDevId = getDeviceId();

  const keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    return { success: false, msg: '❌ Mã kích hoạt không tồn tại! Kiểm tra lại mã.' };
  }

  if (keyObj.status === 'used' && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được kích hoạt trên máy khác (${keyObj.deviceId})!` 
    };
  }

  const nowStr = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');

  // Update Key
  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = nowStr;

  // Update User
  let u = users.find(x => x.deviceId === currentDevId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = cleanKey;
    u.lastActive = nowStr;
  } else {
    users.push({
      deviceId: currentDevId,
      name: `Học viên ${currentDevId}`,
      role: 'vip',
      activatedKey: cleanKey,
      deviceType: currentDevId.includes('IPHO') || currentDevId.includes('MOBI') ? '📱 Điện thoại' : '💻 Thiết bị',
      createdAt: nowStr,
      lastActive: nowStr
    });
  }

  // Save both local & cloud
  localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');
  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  await saveAndPushCloudData(keys, users);

  return { success: true, msg: `🎉 Kích hoạt VIP thành công với mã ${cleanKey}!` };
}

function redeemVipKey(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();
  const keys = getVipKeysDB();
  const currentDevId = getDeviceId();

  const keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    return { success: false, msg: '❌ Mã kích hoạt không tồn tại!' };
  }

  if (keyObj.status === 'used' && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được dùng trên máy khác (${keyObj.deviceId})!` 
    };
  }

  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');
  pushCloudKeysDB(keys);

  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');
  trackCurrentDeviceUser();
  return { success: true, msg: '🎉 Kích hoạt VIP thành công trên thiết bị này!' };
}

// Render Complete Admin Panel with User Management
let currentAdminTab = 'keys';

async function openAdminPanelModal() {
  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  // Render initial loading UI instantly!
  modal.innerHTML = `
    <div class="login-card admin-card" style="text-align: center; padding: 48px 32px;">
      <div class="login-logo" style="background: linear-gradient(135deg, #7c3aed, #4c1d95);"><i class="fa-solid fa-spinner fa-spin"></i></div>
      <h3 style="font-size: 1.2rem; color: #581c87; margin-top: 12px;">Đang tải Dashboard Admin...</h3>
      <p style="font-size: 0.88rem; color: #64748b;">Đang kết nối & đồng bộ dữ liệu Real-time từ Cloud DB</p>
    </div>
  `;
  modal.style.display = 'flex';

  // Fetch real-time Cloud Data asynchronously
  const cloudData = typeof fetchCloudData === 'function' ? await fetchCloudData() : { keys: getVipKeysDB(), users: getUsersDB() };
  const keys = cloudData.keys;
  const users = cloudData.users;

  const vipCount = users.filter(u => u.role === 'vip').length;
  const guestCount = users.filter(u => u.role === 'guest').length;
  const totalUsers = users.length;

  let contentHtml = '';

  if (currentAdminTab === 'keys') {
    let keysRows = keys.map((k) => `
      <tr>
        <td style="font-weight: 800; color: #1d4ed8;">${k.key}</td>
        <td>
          ${k.status === 'used' 
            ? `<span class="badge-status-used">🔴 Đã dùng (${k.deviceId || ''})</span>` 
            : `<span class="badge-status-unused">🟢 Chưa dùng</span>`}
        </td>
        <td style="font-size: 0.78rem; color: #64748b;">${k.createdAt || ''}</td>
        <td>
          <button class="btn-copy-key" onclick="copyKeyToClipboard('${k.key}')" title="Copy mã"><i class="fa-solid fa-copy"></i></button>
          <button class="btn-delete-key" onclick="deleteVipKey('${k.key}')" title="Xóa mã"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `).join('');

    contentHtml = `
      <div class="admin-actions">
        <button class="btn-login-vip" id="btnGenKey" style="background: linear-gradient(135deg, #10b981, #059669);">
          <i class="fa-solid fa-plus-circle"></i> + Tạo Mã VIP Mới
        </button>
      </div>

      <div class="keys-table-container">
        <table class="admin-keys-table">
          <thead>
            <tr>
              <th>Mã VIP</th>
              <th>Trạng thái</th>
              <th>Ngày tạo</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            ${keysRows || '<tr><td colspan="4">Chưa có mã nào. Bấm "+ Tạo Mã VIP Mới" để tạo!</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  } else {
    // Users Management Tab
    let usersRows = users.map((u) => `
      <tr>
        <td style="font-weight: 800; color: #1e3a8a;">
          ${u.deviceId}
          ${u.deviceId === getDeviceId() ? '<span style="font-size: 0.7rem; color: #2563eb;">(Máy này)</span>' : ''}
        </td>
        <td>
          ${u.role === 'vip' 
            ? `<span class="badge-status-unused">👑 VIP</span>` 
            : `<span class="badge-status-used" style="background: #fff7ed; color: #c2410c;">⏱️ Khách</span>`}
        </td>
        <td style="font-size: 0.8rem; font-weight: 700;">${u.activatedKey || 'Không'}</td>
        <td style="font-size: 0.78rem; color: #64748b;">${u.lastActive || ''}</td>
        <td>
          ${u.role !== 'vip' 
            ? `<button class="btn-promote-user" onclick="promoteUserToVip('${u.deviceId}')"><i class="fa-solid fa-crown"></i> Cấp VIP</button>` 
            : `<button class="btn-block-user" onclick="demoteUserToGuest('${u.deviceId}')"><i class="fa-solid fa-lock"></i> Hạ Khách</button>`}
          <button class="btn-delete-key" onclick="deleteUserRecord('${u.deviceId}')" title="Xóa User"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `).join('');

    contentHtml = `
      <div class="keys-table-container">
        <table class="admin-keys-table">
          <thead>
            <tr>
              <th>Thiết Bị / User ID</th>
              <th>Quyền</th>
              <th>Mã Kích Hoạt</th>
              <th>Hoạt động cuối</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            ${usersRows || '<tr><td colspan="5">Chưa có dữ liệu học viên.</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  }

  modal.innerHTML = `
    <div class="login-card admin-card">
      <div class="login-header">
        <div class="login-logo" style="background: linear-gradient(135deg, #7c3aed, #4c1d95);"><i class="fa-solid fa-user-shield"></i></div>
        <h2>TRANG QUẢN TRỊ ADMIN</h2>
        <p>Quản lý Mã VIP & Danh sách Học viên / Thiết bị</p>
      </div>

      <!-- Stats Bar -->
      <div class="admin-stats-row">
        <div class="stat-box">
          <div class="num">${totalUsers}</div>
          <div class="lbl">Tổng Học Viên</div>
        </div>
        <div class="stat-box">
          <div class="num" style="color: #059669;">${vipCount}</div>
          <div class="lbl">Học Viên VIP</div>
        </div>
        <div class="stat-box">
          <div class="num" style="color: #c2410c;">${guestCount}</div>
          <div class="lbl">Khách Dùng Thử</div>
        </div>
      </div>

      <!-- Admin Tabs -->
      <div class="admin-tab-bar">
        <button class="admin-tab-btn ${currentAdminTab === 'keys' ? 'active' : ''}" id="adminTabKeys">
          <i class="fa-solid fa-key"></i> Quản Lý Mã VIP (${keys.length})
        </button>
        <button class="admin-tab-btn ${currentAdminTab === 'users' ? 'active' : ''}" id="adminTabUsers">
          <i class="fa-solid fa-users"></i> Quản Lý Học Viên (${users.length})
        </button>
      </div>

      ${contentHtml}

      <button class="btn-login-guest" id="btnCloseAdmin" style="margin-top: 16px;"><i class="fa-solid fa-xmark"></i> Đóng Trang Admin</button>
    </div>
  `;

  modal.style.display = 'flex';

  // Event Listeners
  const tabKeys = document.getElementById('adminTabKeys');
  const tabUsers = document.getElementById('adminTabUsers');
  const genBtn = document.getElementById('btnGenKey');
  const closeBtn = document.getElementById('btnCloseAdmin');

  if (tabKeys) tabKeys.addEventListener('click', () => { currentAdminTab = 'keys'; refreshAdminUI(); });
  if (tabUsers) tabUsers.addEventListener('click', () => { currentAdminTab = 'users'; refreshAdminUI(); });
  if (genBtn) genBtn.addEventListener('click', async () => {
    genBtn.disabled = true;
    genBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo mã...';
    const newCode = await generateNewVipKey();
    if (typeof showToast === 'function') showToast(`🎉 Đã tạo Mã VIP mới: ${newCode}`, 'success'); else alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);
    await refreshAdminUI();
  });
  if (closeBtn) closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
}

function copyKeyToClipboard(text) {
  navigator.clipboard.writeText(text);
  if (typeof showToast === 'function') showToast(`📋 Đã copy mã VIP: ${text}`, 'info'); else alert(`📋 Đã copy mã VIP: ${text}`);
}

function deleteVipKey(key) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Mã VIP', `Bạn có chắc chắn muốn xóa mã VIP <strong>${key}</strong> khỏi hệ thống?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys.filter(k => k.key.toUpperCase() !== key.toUpperCase());
      let users = cloudData.users;

      // Demote any user that was using this deleted key
      for (let u of users) {
        if (u.activatedKey && u.activatedKey.toUpperCase() === key.toUpperCase()) {
          u.role = 'guest';
          u.activatedKey = 'N/A';
        }
      }

      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa mã VIP ${key}`, 'info');
      await refreshAdminUI();
    });
  }
}

function promoteUserToVip(devId) {
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = 'ADMIN_GRANTED';
    pushCloudKeysDB(getVipKeysDB());

    if (devId === getDeviceId()) {
      localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');
      location.reload();
    } else {
      refreshAdminUI();
    }
  }
}

function demoteUserToGuest(devId) {
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'guest';
    u.activatedKey = 'N/A';
    pushCloudKeysDB(getVipKeysDB());

    if (devId === getDeviceId()) {
      setUserRole('guest');
      location.reload();
    } else {
      refreshAdminUI();
    }
  }
}

function deleteUserRecord(devId) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Học Viên', `Bạn có chắc chắn muốn xóa dữ liệu học viên <strong>${devId}</strong>?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys;
      let users = cloudData.users.filter(u => u.deviceId !== devId);

      // Free up any VIP key bound to this deleted user
      for (let k of keys) {
        if (k.deviceId === devId) {
          k.status = 'unused';
          k.deviceId = null;
        }
      }

      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa học viên ${devId}`, 'info');
      await refreshAdminUI();
    });
  }
}

function promptAdminLogin() {
  window.location.href = 'admin.html';
}

document.addEventListener('DOMContentLoaded', () => {
  trackCurrentDeviceUser();
  if (window.location.search.includes('openAdmin=true')) {
    history.replaceState(null, '', window.location.pathname);
    refreshAdminUI();
  }
});


async function fetchCloudKeysDB() {
  const d = await fetchCloudData();
  return d.keys;
}

async function pushCloudKeysDB(keysToPush) {
  await pushCloudData(keysToPush, getUsersDB());
}