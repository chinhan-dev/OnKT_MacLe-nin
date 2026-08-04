import json, re

# 1. Add User Management Styles to styles.css
user_mgmt_css = """

/* Admin User Management Styles */
.admin-tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
}

.admin-tab-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #f8fafc;
  color: #475569;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.admin-tab-btn.active {
  background-color: #7e22ce;
  color: #ffffff;
  border-color: #7e22ce;
}

.admin-stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.stat-box {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 14px;
  text-align: center;
}

.stat-box .num {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1e3a8a;
}

.stat-box .lbl {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.btn-promote-user {
  padding: 4px 8px;
  border-radius: 6px;
  border: none;
  background-color: #ecfdf5;
  color: #047857;
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
  margin-right: 4px;
}

.btn-block-user {
  padding: 4px 8px;
  border-radius: 6px;
  border: none;
  background-color: #fff7ed;
  color: #c2410c;
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(user_mgmt_css)

print("User Management CSS added to styles.css.")

# 2. Rebuild admin.js with User Management features
admin_full_js = """/* ==========================================================================
   ADMIN PANEL & USER MANAGEMENT SYSTEM (Pass: chinhanxt)
   ========================================================================== */

const ADMIN_PASS = 'chinhanxt';
const VIP_KEYS_STORAGE = 'lms_vip_keys_db';
const USERS_DB_STORAGE = 'lms_users_db';
const DEVICE_ID_KEY = 'lms_device_fingerprint';
const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';

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
function trackCurrentDeviceUser() {
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

  saveUsersDB(users);
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
      { key: 'MAC-VIP888', status: 'unused', deviceId: null, createdAt: new Date().toLocaleDateString('vi-VN') },
      { key: 'MAC-VIP999', status: 'unused', deviceId: null, createdAt: new Date().toLocaleDateString('vi-VN') }
    ];
    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(initialKeys));
    return initialKeys;
  }
  return JSON.parse(data);
}

function saveVipKeysDB(keys) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
}

function generateNewVipKey() {
  const code = 'MAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
  const keys = getVipKeysDB();
  keys.push({
    key: code,
    status: 'unused',
    deviceId: null,
    createdAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN')
  });
  saveVipKeysDB(keys);
  return code;
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
  saveVipKeysDB(keys);

  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  setUserRole('vip');
  trackCurrentDeviceUser();
  return { success: true, msg: '🎉 Kích hoạt VIP thành công trên thiết bị này!' };
}

// Render Complete Admin Panel with User Management
let currentAdminTab = 'keys';

function openAdminPanelModal() {
  trackCurrentDeviceUser();

  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  const keys = getVipKeysDB();
  const users = getUsersDB();

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
        <h2>TRANG QUẢN TRỊ ADMIN (CHỈNH AN)</h2>
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

  if (tabKeys) tabKeys.addEventListener('click', () => { currentAdminTab = 'keys'; openAdminPanelModal(); });
  if (tabUsers) tabUsers.addEventListener('click', () => { currentAdminTab = 'users'; openAdminPanelModal(); });
  if (genBtn) genBtn.addEventListener('click', () => {
    const newCode = generateNewVipKey();
    alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);
    openAdminPanelModal();
  });
  if (closeBtn) closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
}

function copyKeyToClipboard(text) {
  navigator.clipboard.writeText(text);
  alert(`📋 Đã copy mã VIP: ${text}`);
}

function deleteVipKey(key) {
  if (confirm(`Bạn có chắc muốn xóa mã VIP ${key}?`)) {
    let keys = getVipKeysDB();
    keys = keys.filter(k => k.key !== key);
    saveVipKeysDB(keys);
    openAdminPanelModal();
  }
}

function promoteUserToVip(devId) {
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = 'ADMIN_GRANTED';
    saveUsersDB(users);

    if (devId === getDeviceId()) {
      setUserRole('vip');
      location.reload();
    } else {
      openAdminPanelModal();
    }
  }
}

function demoteUserToGuest(devId) {
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'guest';
    u.activatedKey = 'N/A';
    saveUsersDB(users);

    if (devId === getDeviceId()) {
      setUserRole('guest');
      location.reload();
    } else {
      openAdminPanelModal();
    }
  }
}

function deleteUserRecord(devId) {
  if (confirm(`Bạn có chắc muốn xóa dữ liệu học viên ${devId}?`)) {
    let users = getUsersDB();
    users = users.filter(x => x.deviceId !== devId);
    saveUsersDB(users);
    openAdminPanelModal();
  }
}

function promptAdminLogin() {
  const pass = prompt('🔑 Nhập Mật Khẩu Admin (chinhanxt):');
  if (pass === ADMIN_PASS) {
    openAdminPanelModal();
  } else if (pass !== null) {
    alert('❌ Mật khẩu Admin không đúng!');
  }
}

document.addEventListener('DOMContentLoaded', trackCurrentDeviceUser);
"""

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(admin_full_js)

print("Updated admin.js with complete User Management system.")
