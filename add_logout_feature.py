# 1. Add Logout CSS to styles.css
logout_css = """

/* Logout Header Button */
.btn-logout-header {
  padding: 6px 14px;
  border-radius: 9999px;
  background-color: #fef2f2;
  color: #ef4444;
  border: 1px solid #fca5a5;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  margin-left: 6px;
}

.btn-logout-header:hover {
  background-color: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(logout_css)

print("Logout CSS added to styles.css.")

# 2. Update auth.js to render Logout button and handle logout event
with open('auth.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace renderUserBadge function
old_render = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badge = document.getElementById('userAuthBadge');
  if (!badge) {
    badge = document.createElement('div');
    badge.id = 'userAuthBadge';
    controls.insertBefore(badge, controls.firstChild);
  }

  if (role === 'vip') {
    badge.className = 'user-auth-status vip';
    badge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Đã có quyền (VIP)`;
  } else if (role === 'guest') {
    const remaining = getGuestTimeRemaining();
    badge.className = 'user-auth-status guest';
    badge.innerHTML = `<i class="fa-solid fa-clock"></i> Khách: <span class="timer-count" id="guestCountdown">${formatTime(remaining)}</span>`;
  }
}"""

new_render = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badgeWrapper = document.getElementById('userAuthWrapper');
  if (!badgeWrapper) {
    badgeWrapper = document.createElement('div');
    badgeWrapper.id = 'userAuthWrapper';
    badgeWrapper.style.display = 'inline-flex';
    badgeWrapper.style.alignItems = 'center';
    badgeWrapper.style.gap = '8px';
    controls.insertBefore(badgeWrapper, controls.firstChild);
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
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;

  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}

function handleLogout() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  if (guestInterval) clearInterval(guestInterval);
  location.reload();
}"""

code = code.replace(old_render, new_render)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("auth.js updated with Logout button functionality.")
