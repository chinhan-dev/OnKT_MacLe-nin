
/* ==========================================================================
   ADMIN PANEL & SINGLE-DEVICE VIP KEY SYSTEM (Pass: chinhanxt)
   ========================================================================== */

const ADMIN_PASS = 'chinhanxt';
const VIP_KEYS_STORAGE = 'lms_vip_keys_db';
const DEVICE_ID_KEY = 'lms_device_fingerprint';
const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';

// Generate or retrieve unique device fingerprint
function getDeviceId() {
  let devId = localStorage.getItem(DEVICE_ID_KEY);
  if (!devId) {
    const randomStr = Math.random().toString(36).substring(2, 9).toUpperCase();
    const platform = (navigator.platform || 'DEV').replace(/[^a-zA-Z0-9]/g, '').substring(0, 4).toUpperCase();
    devId = `${platform}-${randomStr}`;
    localStorage.setItem(DEVICE_ID_KEY, devId);
  }
  return devId;
}

// Get all keys from DB
function getVipKeysDB() {
  const data = localStorage.getItem(VIP_KEYS_STORAGE);
  if (!data) {
    // Initial sample keys
    const initialKeys = [
      { key: 'MAC-VIP888', status: 'unused', deviceId: null, createdAt: new Date().toISOString() },
      { key: 'MAC-VIP999', status: 'unused', deviceId: null, createdAt: new Date().toISOString() }
    ];
    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(initialKeys));
    return initialKeys;
  }
  return JSON.parse(data);
}

function saveVipKeysDB(keys) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
}

// Generate new random VIP key
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

// Verify and activate VIP key for current device
function redeemVipKey(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();
  const keys = getVipKeysDB();
  const currentDevId = getDeviceId();

  const keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    return { success: false, msg: '❌ Mã kích hoạt không tồn tại! Vui lòng kiểm tra lại.' };
  }

  if (keyObj.status === 'used' && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được kích hoạt trên thiết bị khác (${keyObj.deviceId})! Không thể chia sẻ cho máy này.` 
    };
  }

  // Bind key to current device
  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');
  saveVipKeysDB(keys);

  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  setUserRole('vip');
  return { success: true, msg: '🎉 Kích hoạt VIP thành công trên thiết bị này!' };
}

// Render Admin Panel Modal
function openAdminPanelModal() {
  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  const role = getUserRole();
  const currentDevId = getDeviceId();
  const keys = getVipKeysDB();

  let keysRows = keys.map((k, idx) => `
    <tr>
      <td style="font-weight: 800; color: #1d4ed8;">${k.key}</td>
      <td>
        ${k.status === 'used' 
          ? `<span class="badge-status-used">🔴 Đã dùng (${k.deviceId})</span>` 
          : `<span class="badge-status-unused">🟢 Chưa dùng</span>`}
      </td>
      <td style="font-size: 0.8rem; color: #64748b;">${k.createdAt || ''}</td>
      <td>
        <button class="btn-copy-key" onclick="copyKeyToClipboard('${k.key}')" title="Copy mã"><i class="fa-solid fa-copy"></i></button>
        <button class="btn-delete-key" onclick="deleteVipKey('${k.key}')" title="Xóa mã"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join('');

  modal.innerHTML = `
    <div class="login-card admin-card">
      <div class="login-header">
        <div class="login-logo" style="background: linear-gradient(135deg, #7c3aed, #4c1d95);"><i class="fa-solid fa-user-shield"></i></div>
        <h2>TRANG QUẢN TRỊ ADMIN (CHỈNH AN)</h2>
        <p>Tạo & Quản lý Mã VIP 1 Thiết Bị cho Khách hàng</p>
      </div>

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

      <button class="btn-login-guest" id="btnCloseAdmin"><i class="fa-solid fa-xmark"></i> Đóng Trang Admin</button>
    </div>
  `;

  modal.style.display = 'flex';

  document.getElementById('btnGenKey').addEventListener('click', () => {
    const newCode = generateNewVipKey();
    alert(`🎉 Đã tạo Mã VIP mới: ${newCode}
Đã lưu vào danh sách!`);
    openAdminPanelModal();
  });

  document.getElementById('btnCloseAdmin').addEventListener('click', () => {
    modal.style.display = 'none';
  });
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

// Prompt for Admin Password "chinhanxt"
function promptAdminLogin() {
  const pass = prompt('🔑 Nhập Mật Khẩu Admin (chinhanxt):');
  if (pass === ADMIN_PASS) {
    openAdminPanelModal();
  } else if (pass !== null) {
    alert('❌ Mật khẩu Admin không đúng!');
  }
}
