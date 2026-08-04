import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

new_prompt_admin = """function promptAdminLogin() {
  const loginModal = document.getElementById('loginModal');
  if (loginModal) loginModal.style.display = 'none';

  let modal = document.getElementById('adminPassModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminPassModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }
  modal.style.zIndex = '99999';

  modal.innerHTML = `
    <div class="login-card" style="max-width: 400px; padding: 32px 28px;">
      <div class="login-header">
        <div class="login-logo" style="background: linear-gradient(135deg, #7c3aed, #4c1d95); width: 60px; height: 60px; font-size: 26px;">
          <i class="fa-solid fa-user-shield"></i>
        </div>
        <h2 style="font-size: 1.25rem; color: #581c87;">ĐĂNG NHẬP QUẢN TRỊ ADMIN</h2>
        <p style="font-size: 0.85rem; color: #64748b;">Vui lòng nhập mật khẩu Admin để truy cập Dashboard</p>
      </div>

      <div class="pass-input-group" style="display: flex; gap: 8px; margin-top: 8px;">
        <input type="password" id="adminPassInputModal" placeholder="Nhập mật khẩu Admin..." style="flex: 1; padding: 12px 14px; border-radius: 12px; border: 2px solid #7c3aed; font-size: 0.95rem; outline: none;">
        <button id="adminPassSubmitModal" style="padding: 12px 18px; background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border: none; border-radius: 12px; font-weight: 800; cursor: pointer;">
          <i class="fa-solid fa-arrow-right"></i>
        </button>
      </div>

      <p class="pass-error" id="adminPassErrorModal" style="display: none; color: #dc2626; font-size: 0.85rem; font-weight: 700; margin-top: 6px;">❌ Mật khẩu Admin không đúng!</p>

      <button id="adminPassCloseModal" class="btn-login-guest" style="margin-top: 12px; padding: 10px; border-radius: 10px; font-size: 0.88rem;">Hủy bỏ</button>
    </div>
  `;

  modal.style.display = 'flex';

  const input = document.getElementById('adminPassInputModal');
  const submitBtn = document.getElementById('adminPassSubmitModal');
  const closeBtn = document.getElementById('adminPassCloseModal');
  const err = document.getElementById('adminPassErrorModal');

  input.focus();

  function verifyAdminPass() {
    const entered = input.value.trim();
    if (entered === ADMIN_PASS) {
      modal.style.display = 'none';
      localStorage.setItem('lms_is_admin', 'true');
      setUserRole('vip');
      openAdminPanelModal();
    } else {
      err.style.display = 'block';
    }
  }

  submitBtn.addEventListener('click', verifyAdminPass);
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyAdminPass();
  });
  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    const role = typeof getUserRole === 'function' ? getUserRole() : null;
    if (!role) {
      const lm = document.getElementById('loginModal');
      if (lm) lm.style.display = 'flex';
    }
  });
}"""

pattern_prompt = r"function promptAdminLogin\(\) \{.*?\n\}"
code = re.sub(pattern_prompt, new_prompt_admin.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with z-index 99999 for Admin Password Modal.")
