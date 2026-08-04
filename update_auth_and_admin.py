import re

# Add Admin Panel CSS to styles.css
admin_css = """

/* Admin Panel Styles */
.admin-card {
  max-width: 600px !important;
}

.admin-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.keys-table-container {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background-color: #ffffff;
}

.admin-keys-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  text-align: left;
}

.admin-keys-table th, .admin-keys-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #e2e8f0;
}

.admin-keys-table th {
  background-color: #f1f5f9;
  color: #1e293b;
  font-weight: 800;
  position: sticky;
  top: 0;
}

.badge-status-unused {
  background-color: #ecfdf5;
  color: #047857;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.75rem;
}

.badge-status-used {
  background-color: #fef2f2;
  color: #b91c1c;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.75rem;
}

.btn-copy-key, .btn-delete-key {
  padding: 4px 8px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  margin-right: 4px;
}

.btn-copy-key { background-color: #eff6ff; color: #2563eb; }
.btn-delete-key { background-color: #fef2f2; color: #ef4444; }

.btn-admin-header {
  padding: 6px 12px;
  border-radius: 9999px;
  background-color: #f3e8ff;
  color: #7e22ce;
  border: 1px solid #d8b4fe;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-admin-header:hover {
  background-color: #7e22ce;
  color: #ffffff;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(admin_css)

print("Admin CSS added to styles.css.")

# Update auth.js to handle VIP Redeem Keys & Admin Button
with open('auth.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Update showLoginModal in auth.js
old_modal_html = """  modal.innerHTML = `
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo"><i class="fa-solid fa-shield-halved"></i></div>
        <h2>ĐĂNG NHẬP HỆ THỐNG LMS</h2>
        ${msgHtml}
      </div>

      <div class="login-options">
        <div class="option-box">
          <button class="btn-login-vip" id="loginVipBtn">
            <i class="fa-solid fa-key"></i> Đã Có Quyền (Nhập Mật Khẩu)
          </button>
          <div class="pass-input-group" id="passGroup" style="display: none;">
            <input type="password" id="vipPasswordInput" placeholder="Nhập mật khẩu...">
            <button id="submitVipPassBtn"><i class="fa-solid fa-arrow-right"></i></button>
          </div>
          <p class="pass-error" id="passErrorMsg" style="display: none;">❌ Mật khẩu không chính xác!</p>
        </div>

        <div class="option-box">
          <button class="btn-login-guest" id="loginGuestBtn">
            <i class="fa-solid fa-user-clock"></i> Khách (Thao tác 5 phút)
          </button>
        </div>
      </div>
    </div>
  `;"""

new_modal_html = """  modal.innerHTML = `
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo"><i class="fa-solid fa-shield-halved"></i></div>
        <h2>ĐĂNG NHẬP HỆ THỐNG LMS</h2>
        ${msgHtml}
      </div>

      <div class="login-options">
        <div class="option-box">
          <button class="btn-login-vip" id="loginVipBtn">
            <i class="fa-solid fa-key"></i> Đã Có Quyền (Nhập Mã VIP 1 Thiết Bị)
          </button>
          <div class="pass-input-group" id="passGroup" style="display: none;">
            <input type="text" id="vipPasswordInput" placeholder="Nhập mã VIP (VD: MAC-VIP888)..." style="text-transform: uppercase;">
            <button id="submitVipPassBtn"><i class="fa-solid fa-arrow-right"></i> Kích hoạt</button>
          </div>
          <p class="pass-error" id="passErrorMsg" style="display: none;">❌ Mã không hợp lệ hoặc đã dùng trên máy khác!</p>
        </div>

        <div class="option-box">
          <button class="btn-login-guest" id="loginGuestBtn">
            <i class="fa-solid fa-user-clock"></i> Khách (Dùng thử 5 phút)
          </button>
        </div>

        <div style="margin-top: 10px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
          <button class="btn-admin-header" onclick="promptAdminLogin()">
            <i class="fa-solid fa-user-gear"></i> Đăng nhập Admin Quản Lý Mã (chinhanxt)
          </button>
        </div>
      </div>
    </div>
  `;"""

code = code.replace(old_modal_html, new_modal_html)

# Update handleVipSubmit in auth.js
old_handle_vip = """  function handleVipSubmit() {
    const entered = passInput.value.trim();
    if (entered === 'chinhanxt') {
      setUserRole('vip');
      modal.style.display = 'none';
      location.reload();
    } else {
      passErr.style.display = 'block';
    }
  }"""

new_handle_vip = """  function handleVipSubmit() {
    const entered = passInput.value.trim();
    if (!entered) return;

    // Check if master admin pass entered directly
    if (entered === 'chinhanxt') {
      setUserRole('vip');
      modal.style.display = 'none';
      location.reload();
      return;
    }

    // Check device-bound VIP key
    const res = redeemVipKey(entered);
    if (res.success) {
      alert(res.msg);
      modal.style.display = 'none';
      location.reload();
    } else {
      passErr.textContent = res.msg;
      passErr.style.display = 'block';
    }
  }"""

code = code.replace(old_handle_vip, new_handle_vip)

# Also update renderUserBadge in auth.js to include Admin button
old_render_user = """  badgeWrapper.innerHTML = `
    ${badgeContent}
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;"""

new_render_user = """  badgeWrapper.innerHTML = `
    ${badgeContent}
    <button class="btn-admin-header" onclick="promptAdminLogin()" title="Trang Quản Trị Admin (chinhanxt)">
      <i class="fa-solid fa-user-gear"></i> Admin
    </button>
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;"""

code = code.replace(old_render_user, new_render_user)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated auth.js with Admin & 1-Device VIP Key logic.")

