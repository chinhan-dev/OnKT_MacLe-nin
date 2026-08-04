import re

# 1. Update auth.js
with open('auth.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace renderUserBadge with sleek User Capsule
old_badge_render = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badgeWrapper = document.getElementById('userAuthWrapper');
  if (!badgeWrapper) {
    badgeWrapper = document.createElement('div');
    badgeWrapper.id = 'userAuthWrapper';
    badgeWrapper.className = 'user-auth-wrapper';
    controls.appendChild(badgeWrapper);
  }

  let badgeContent = '';
  if (role === 'vip') {
    badgeContent = `<div class="user-auth-status vip"><i class="fa-solid fa-circle-check"></i> Đã có quyền (VIP)</div>`;
  } else if (role === 'guest') {
    const remaining = getGuestTimeRemaining();
    badgeContent = `<div class="user-auth-status guest"><i class="fa-solid fa-clock"></i> Khách: <span class="timer-count" id="guestCountdown">${formatTime(remaining)}</span></div>`;
  }

  badgeWrapper.innerHTML = `
    ${badgeContent}
    <button class="btn-admin-header" onclick="promptAdminLogin()" title="Trang Quản Trị Admin (chinhanxt)">
      <i class="fa-solid fa-user-gear"></i> Admin
    </button>
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;

  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}"""

new_badge_render = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badgeWrapper = document.getElementById('userAuthWrapper');
  if (!badgeWrapper) {
    badgeWrapper = document.createElement('div');
    badgeWrapper.id = 'userAuthWrapper';
    badgeWrapper.className = 'user-auth-wrapper';
    controls.appendChild(badgeWrapper);
  }

  let capsuleHtml = '';
  if (role === 'vip') {
    capsuleHtml = `
      <div class="user-capsule vip">
        <i class="fa-solid fa-circle-check"></i>
        <span>VIP</span>
        <span class="capsule-divider"></span>
        <button class="btn-logout-icon" id="logoutBtn" title="Đăng xuất"><i class="fa-solid fa-right-from-bracket"></i></button>
      </div>
    `;
  } else if (role === 'guest') {
    const remaining = getGuestTimeRemaining();
    capsuleHtml = `
      <div class="user-capsule guest">
        <i class="fa-solid fa-clock"></i>
        <span>Khách: <strong id="guestCountdown" style="font-family: monospace;">${formatTime(remaining)}</strong></span>
        <span class="capsule-divider"></span>
        <button class="btn-logout-icon" id="logoutBtn" title="Đăng xuất"><i class="fa-solid fa-right-from-bracket"></i></button>
      </div>
    `;
  }

  badgeWrapper.innerHTML = `
    <button class="btn-admin-header" onclick="promptAdminLogin()" title="Trang Quản Trị Admin">
      <i class="fa-solid fa-user-gear"></i> Admin
    </button>
    ${capsuleHtml}
  `;

  const lBtn = document.getElementById('logoutBtn');
  if (lBtn) lBtn.addEventListener('click', handleLogout);
}"""

code = code.replace(old_badge_render, new_badge_render)

# Replace alerts with showToast in auth.js
code = code.replace("alert(res.msg);", "if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);")

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated auth.js with User Capsule and Toast notifications.")

# 2. Update admin.js to replace alert() and confirm()
with open('admin.js', 'r', encoding='utf-8') as f:
    acode = f.read()

acode = acode.replace("alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);", "if (typeof showToast === 'function') showToast(`🎉 Đã tạo Mã VIP mới: ${newCode}`, 'success'); else alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);")
acode = acode.replace("alert(`📋 Đã copy mã VIP: ${text}`);", "if (typeof showToast === 'function') showToast(`📋 Đã copy mã VIP: ${text}`, 'info'); else alert(`📋 Đã copy mã VIP: ${text}`);")

# Replace deleteVipKey with custom confirm
old_del_key = """function deleteVipKey(key) {
  if (confirm(`Bạn có chắc muốn xóa mã VIP ${key}?`)) {
    let keys = getVipKeysDB();
    keys = keys.filter(k => k.key !== key);
    saveVipKeysDB(keys);
    openAdminPanelModal();
  }
}"""

new_del_key = """function deleteVipKey(key) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Mã VIP', `Bạn có chắc chắn muốn xóa mã VIP <strong>${key}</strong> khỏi hệ thống?`, () => {
      let keys = getVipKeysDB();
      keys = keys.filter(k => k.key !== key);
      saveVipKeysDB(keys);
      openAdminPanelModal();
      showToast(`🗑️ Đã xóa mã VIP ${key}`, 'info');
    });
  } else {
    if (confirm(`Xóa mã ${key}?`)) {
      let keys = getVipKeysDB();
      keys = keys.filter(k => k.key !== key);
      saveVipKeysDB(keys);
      openAdminPanelModal();
    }
  }
}"""

acode = acode.replace(old_del_key, new_del_key)

# Replace deleteUserRecord with custom confirm
old_del_user = """function deleteUserRecord(devId) {
  if (confirm(`Bạn có chắc muốn xóa dữ liệu học viên ${devId}?`)) {
    let users = getUsersDB();
    users = users.filter(x => x.deviceId !== devId);
    saveUsersDB(users);
    openAdminPanelModal();
  }
}"""

new_del_user = """function deleteUserRecord(devId) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Học Viên', `Bạn có chắc chắn muốn xóa dữ liệu học viên <strong>${devId}</strong>?`, () => {
      let users = getUsersDB();
      users = users.filter(x => x.deviceId !== devId);
      saveUsersDB(users);
      openAdminPanelModal();
      showToast(`🗑️ Đã xóa học viên ${devId}`, 'info');
    });
  } else {
    if (confirm(`Xóa học viên ${devId}?`)) {
      let users = getUsersDB();
      users = users.filter(x => x.deviceId !== devId);
      saveUsersDB(users);
      openAdminPanelModal();
    }
  }
}"""

acode = acode.replace(old_del_user, new_del_user)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated admin.js with custom Toast and Confirm Modal.")

