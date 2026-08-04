async function refreshAdminUI() {
  if (window.location.pathname.endsWith('admin.html') && typeof renderAdminStandalonePage === 'function') {
    await renderAdminStandalonePage();
  } else if (typeof openAdminPanelModal === 'function') {
    await openAdminPanelModal();
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
const DEFAULT_GG_SHEET_URL = '/api/sheet';
const GG_SHEET_URL_STORAGE = 'lms_gg_sheet_script_url';

function getCloudEndpoint() {
  const custom = localStorage.getItem(GG_SHEET_URL_STORAGE);
  if (custom && custom.includes('script.google.com')) {
    localStorage.removeItem(GG_SHEET_URL_STORAGE);
    return '/api/sheet';
  }
  return custom || DEFAULT_GG_SHEET_URL;
}

// Save & Overwrite Cloud DB / Google Sheets Directly via /api/sheet Proxy
async function saveAndPushCloudData(keys, users) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));

  const endpoint = getCloudEndpoint();
  try {
    const fetchOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keys: keys, users: users })
    };

    const putRes = await fetch(endpoint, fetchOptions);
    if (putRes.ok) {
      console.log('Cloud DB / Google Sheet proxy save confirmed.');
    }
  } catch (e) {
    console.warn('Cloud DB / Google Sheet proxy save error:', e);
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

// Fetch Both Keys & Users from Cloud DB / Google Sheets Proxy & Merge Cleanly
async function fetchCloudData() {
  const endpoint = getCloudEndpoint();
  const lKeys = getVipKeysDB();
  const lUsers = getUsersDB();

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 10000);

    const res = await fetch(endpoint, { cache: 'no-store', signal: controller.signal });
    clearTimeout(timer);

    if (res.ok) {
      const json = await res.json();
      if (json && (json.status === 'success' || json.keys)) {
        const dbObj = json.data || json;
        const cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        const cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];

        // Map-based Smart Merge
        const keyMap = new Map();
        lKeys.forEach(k => { if (k && k.key) keyMap.set(k.key.toUpperCase(), k); });
        cloudKeys.forEach(k => { if (k && k.key) keyMap.set(k.key.toUpperCase(), k); });

        const userMap = new Map();
        lUsers.forEach(u => { if (u && u.deviceId) userMap.set(u.deviceId, u); });
        cloudUsers.forEach(u => { if (u && u.deviceId) userMap.set(u.deviceId, u); });

        const finalKeys = Array.from(keyMap.values());
        const finalUsers = Array.from(userMap.values());

        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(finalKeys));
        localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(finalUsers));

        return { keys: finalKeys, users: finalUsers, fromCloud: true };
      }
    }
  } catch (e) {
    console.warn('Cloud DB / Google Sheet fetch offline/timeout, using local storage.', e);
  }

  return { keys: lKeys, users: aggregateUsersFromKeys(lKeys, lUsers), fromCloud: false };
}

// Push Both Keys & Users to Cloud DB Safely with Merge
async function pushCloudData(keysToPush, usersToPush) {
  const keys = keysToPush || getVipKeysDB();
  const users = usersToPush || getUsersDB();
  await saveAndPushCloudData(keys, users);
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
  const role = typeof getUserRole === 'function' ? getUserRole() || 'guest' : localStorage.getItem('lms_user_role') || 'guest';
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
  if (!data) return [];
  return JSON.parse(data);
}

function saveUsersDB(users) {
  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));
}

// Keys DB
function getVipKeysDB() {
  const data = localStorage.getItem(VIP_KEYS_STORAGE);
  if (!data) return [];
  return JSON.parse(data);
}

function saveVipKeysDB(keys) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
}

async function generateNewVipKey() {
  if (localStorage.getItem('lms_is_admin') !== 'true') return null;
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
  
  // Admin Password Shortcut
  if (cleanKey === 'CHINHANXT') {
    localStorage.setItem('lms_is_admin', 'true');
    if (typeof setUserRole === 'function') setUserRole('vip'); else localStorage.setItem('lms_user_role', 'vip');
    return { success: true, msg: '🎉 Đăng nhập Admin thành công!' };
  }

  const currentDevId = getDeviceId();

  // 1. Fetch Cloud DB / Google Sheets Proxy to get latest keys from all devices
  let cloudFetchRes = await fetchCloudData();
  let keys = cloudFetchRes.keys || [];
  let users = cloudFetchRes.users || [];

  let keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    if (!cloudFetchRes.fromCloud && keys.length === 0) {
      return { success: false, msg: `❌ Không kết nối được hệ thống xác minh mã "${cleanKey}". Vui lòng kiểm tra lại mạng!` };
    }
    return { success: false, msg: `❌ Mã "${cleanKey}" không tồn tại trên hệ thống! Vui lòng kiểm tra lại.` };
  }

  // 2. Strict 1 Key = 1 Device Check
  if (keyObj.status === 'used' && keyObj.deviceId && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được kích hoạt trên thiết bị khác (${keyObj.deviceId})! Key chỉ dùng cho 1 thiết bị.` 
    };
  }

  const nowStr = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');

  // Update Key Status
  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = nowStr;

  // Update User Status
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

  // Set VIP role locally
  if (typeof setUserRole === 'function') setUserRole('vip'); else localStorage.setItem('lms_user_role', 'vip');
  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  
  // Save local & push to Cloud Proxy
  saveAndPushCloudData(keys, users);

  return { success: true, msg: `🎉 Kích hoạt VIP thành công với mã ${cleanKey}!` };
}

function redeemVipKey(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();

  if (cleanKey === 'CHINHANXT') {
    localStorage.setItem('lms_is_admin', 'true');
    if (typeof setUserRole === 'function') setUserRole('vip'); else localStorage.setItem('lms_user_role', 'vip');
    return { success: true, msg: '🎉 Đăng nhập Admin thành công!' };
  }

  const keys = getVipKeysDB();
  const currentDevId = getDeviceId();

  const keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    return { success: false, msg: `❌ Mã "${cleanKey}" không tồn tại!` };
  }

  if (keyObj.status === 'used' && keyObj.deviceId && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được dùng trên máy khác (${keyObj.deviceId})! Key chỉ dùng cho 1 thiết bị.` 
    };
  }

  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');
  pushCloudKeysDB(keys);

  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  if (typeof setUserRole === 'function') setUserRole('vip'); else localStorage.setItem('lms_user_role', 'vip');
  trackCurrentDeviceUser();
  return { success: true, msg: '🎉 Kích hoạt VIP thành công trên thiết bị này!' };
}

let currentAdminTab = 'keys';

function copyKeyToClipboard(text) {
  navigator.clipboard.writeText(text);
  if (typeof showToast === 'function') showToast(`📋 Đã copy mã VIP: ${text}`, 'info'); else alert(`📋 Đã copy mã VIP: ${text}`);
}

function deleteVipKey(key) {
  if (localStorage.getItem('lms_is_admin') !== 'true') return;
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Mã VIP', `Bạn có chắc chắn muốn xóa mã VIP <strong>${key}</strong> khỏi hệ thống?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys.filter(k => k.key.toUpperCase() !== key.toUpperCase());
      let users = cloudData.users;

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
  if (localStorage.getItem('lms_is_admin') !== 'true') return;
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = 'ADMIN_GRANTED';
    pushCloudKeysDB(getVipKeysDB());

    if (devId === getDeviceId()) {
      if (typeof setUserRole === 'function') setUserRole('vip'); else localStorage.setItem('lms_user_role', 'vip');
      location.reload();
    } else {
      refreshAdminUI();
    }
  }
}

function demoteUserToGuest(devId) {
  if (localStorage.getItem('lms_is_admin') !== 'true') return;
  let users = getUsersDB();
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'guest';
    u.activatedKey = 'N/A';
    pushCloudKeysDB(getVipKeysDB());

    if (devId === getDeviceId()) {
      if (typeof setUserRole === 'function') setUserRole('guest'); else localStorage.setItem('lms_user_role', 'guest');
      location.reload();
    } else {
      refreshAdminUI();
    }
  }
}

function deleteUserRecord(devId) {
  if (localStorage.getItem('lms_is_admin') !== 'true') return;
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Học Viên', `Bạn có chắc chắn muốn xóa dữ liệu học viên <strong>${devId}</strong>?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys;
      let users = cloudData.users.filter(u => u.deviceId !== devId);

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

function initAdminScript() {
  trackCurrentDeviceUser();
  if (window.location.search.includes('openAdmin=true')) {
    history.replaceState(null, '', window.location.pathname);
    refreshAdminUI();
  }
}

if (document.readyState === 'interactive' || document.readyState === 'complete') {
  initAdminScript();
} else {
  document.addEventListener('DOMContentLoaded', initAdminScript);
}

async function fetchCloudKeysDB() {
  const d = await fetchCloudData();
  return d.keys;
}

async function pushCloudKeysDB(keysToPush) {
  await pushCloudData(keysToPush, getUsersDB());
}