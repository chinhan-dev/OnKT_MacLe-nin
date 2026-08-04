/* ==========================================================================
   AUTH & GUEST TIMER MANAGER (VIP Pass & 5-Min Trial)
   ========================================================================== */

const AUTH_KEY = 'lms_user_role';
const GUEST_TIMER_KEY = 'lms_guest_timer_secs';
const GUEST_MAX_TIME = 300; // 5 minutes in seconds
const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';

let guestInterval = null;

function getUserRole() {
  return localStorage.getItem(AUTH_KEY) || null;
}

function setUserRole(role) {
  localStorage.removeItem('lms_user_logged_out');
  localStorage.setItem(AUTH_KEY, role);
  if (role === 'guest') {
    localStorage.setItem(GUEST_TIMER_KEY, GUEST_MAX_TIME.toString());
    localStorage.removeItem('lms_guest_expired');
  } else {
    localStorage.removeItem(GUEST_TIMER_KEY);
    localStorage.removeItem('lms_guest_expired');
  }
}

function getGuestTimeRemaining() {
  const val = localStorage.getItem(GUEST_TIMER_KEY);
  if (val === null) return GUEST_MAX_TIME;
  const parsed = parseInt(val, 10);
  return isNaN(parsed) ? GUEST_MAX_TIME : parsed;
}

function formatTime(seconds) {
  const secs = Math.max(0, seconds);
  const m = Math.floor(secs / 60).toString().padStart(2, '0');
  const s = (secs % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

async function initAuthSystem() {
  const isLoginPage = window.location.pathname.endsWith('login.html');
  const isAdminPage = window.location.pathname.endsWith('admin.html');
  const isLoggedOut = localStorage.getItem('lms_user_logged_out') === 'true';
  const isGuestExpired = localStorage.getItem('lms_guest_expired') === 'true';
  const isAdmin = localStorage.getItem('lms_is_admin') === 'true';

  if (isAdminPage) {
    if (isAdmin) {
      applyRolePermissions('vip');
    }
    return;
  }

  if (isLoggedOut || isGuestExpired) {
    if (!isLoginPage) {
      window.location.href = 'login.html';
    }
    return;
  }

  let role = getUserRole();

  // If user is Master Admin, always grant VIP access
  if (isAdmin) {
    applyRolePermissions('vip');
    if (isLoginPage) window.location.href = 'index.html';
    return;
  }

  // Check Cloud DB for VIP device activation status verification
  if (role === 'vip' && typeof fetchCloudData === 'function') {
    try {
      const cloudData = await fetchCloudData();
      const devId = typeof getDeviceId === 'function' ? getDeviceId() : null;
      if (devId) {
        const u = cloudData.users.find(x => x.deviceId === devId);
        if (!u || u.role !== 'vip') {
          // Device is not VIP in Cloud DB -> revoke local VIP
          localStorage.removeItem(AUTH_KEY);
          localStorage.removeItem(ACTIVATED_KEY_STORAGE);
          role = null;
        }
      }
    } catch (e) {
      console.warn('Could not verify VIP role with Cloud DB:', e);
    }
  }

  if (!role) {
    if (!isLoginPage) {
      window.location.href = 'login.html';
    }
  } else {
    if (isLoginPage) {
      window.location.href = 'index.html';
    } else {
      if (role === 'guest') {
        const remaining = getGuestTimeRemaining();
        if (remaining <= 0) {
          localStorage.setItem('lms_guest_expired', 'true');
          localStorage.removeItem(AUTH_KEY);
          window.location.href = 'login.html';
          return;
        }
      }
      applyRolePermissions(role);
    }
  }
}

function showLoginModal(expiredMsg = false) {
  let modal = document.getElementById('loginModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'loginModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  const msgHtml = expiredMsg 
    ? `<p style="color: #dc2626; font-weight: 800; background: #fef2f2; padding: 10px; border-radius: 8px; border: 1px solid #fca5a5; margin-bottom: 10px;">
        ⚠️ HẾT THỜI GIAN 5 PHÚT THAO TÁC CHO KHÁCH!<br>Vui lòng nhập Mã VIP 1 Thiết Bị để tiếp tục sử dụng.
       </p>` 
    : '<p>Chọn phương thức đăng nhập để bắt đầu ôn luyện</p>';

  modal.innerHTML = `
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo"><i class="fa-solid fa-shield-halved"></i></div>
        <h2>ĐĂNG NHẬP HỆ THỐNG LMS</h2>
        ${msgHtml}
      </div>

      <div class="login-options">
        <div class="option-box">
          <button class="btn-login-vip" id="loginVipBtn">
            <i class="fa-solid fa-key"></i> Đã Có Mã VIP (1 Thiết Bị)
          </button>
          <div class="pass-input-group" id="passGroup" style="display: none;">
            <input type="text" id="vipPasswordInput" placeholder="Nhập mã VIP (VD: MAC-XXXXXX)..." style="text-transform: uppercase;">
            <button id="submitVipPassBtn"><i class="fa-solid fa-arrow-right"></i> Kích hoạt</button>
          </div>
          <p class="pass-error" id="passErrorMsg" style="display: none;"></p>
        </div>

        <div class="option-box">
          <button class="btn-login-guest" id="loginGuestBtn">
            <i class="fa-solid fa-user-clock"></i> Khách (Dùng thử 5 phút)
          </button>
        </div>

        <div style="margin-top: 10px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
          <button class="btn-admin-header" onclick="promptAdminLogin()">
            <i class="fa-solid fa-user-gear"></i> Đăng nhập Quản Trị Admin
          </button>
        </div>
      </div>
    </div>
  `;

  modal.style.display = 'flex';

  const vipBtn = document.getElementById('loginVipBtn');
  const passGroup = document.getElementById('passGroup');
  const passInput = document.getElementById('vipPasswordInput');
  const submitPass = document.getElementById('submitVipPassBtn');
  const passErr = document.getElementById('passErrorMsg');
  const guestBtn = document.getElementById('loginGuestBtn');

  vipBtn.addEventListener('click', () => {
    passGroup.style.display = 'flex';
    passInput.focus();
  });

  async function handleVipSubmit() {
    const entered = passInput.value.trim();
    if (!entered) return;

    passErr.style.display = 'none';

    if (entered === 'chinhanxt') {
      localStorage.setItem('lms_is_admin', 'true');
      setUserRole('vip');
      modal.style.display = 'none';
      location.reload();
      return;
    }

    submitPass.disabled = true;
    submitPass.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Kích hoạt...';

    try {
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Mạng quá chậm, vui lòng thử lại!')), 5000)
      );

      const redeemPromise = typeof redeemVipKeyAsync === 'function' 
        ? redeemVipKeyAsync(entered) 
        : Promise.resolve(redeemVipKey(entered));

      const res = await Promise.race([redeemPromise, timeoutPromise]);

      if (res.success) {
        if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);
        modal.style.display = 'none';
        setTimeout(() => { location.reload(); }, 400);
      } else {
        passErr.textContent = res.msg;
        passErr.style.display = 'block';
      }
    } catch (err) {
      passErr.textContent = '❌ ' + (err.message || 'Lỗi kết nối, vui lòng thử lại!');
      passErr.style.display = 'block';
    } finally {
      submitPass.disabled = false;
      submitPass.innerHTML = '<i class="fa-solid fa-arrow-right"></i> Kích hoạt';
    }
  }

  submitPass.addEventListener('click', handleVipSubmit);
  passInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleVipSubmit();
  });

  guestBtn.addEventListener('click', () => {
    setUserRole('guest');
    modal.style.display = 'none';
    location.reload();
  });
}

function applyRolePermissions(role) {
  renderUserBadge(role);

  if (role === 'guest') {
    startGuestTimer();
    restrictGuestPage();
  }
}

function updateGuestCountdownDisplay(remaining) {
  const el = document.getElementById('guestCountdown');
  if (el) {
    const timeVal = remaining !== undefined ? remaining : getGuestTimeRemaining();
    el.textContent = formatTime(timeVal);
  }
}

function renderUserBadge(role) {
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
    badgeContent = `<div class="user-auth-status vip"><i class="fa-solid fa-crown"></i> VIP (Đã kích hoạt)</div>`;
  } else if (role === 'guest') {
    const remaining = getGuestTimeRemaining();
    badgeContent = `<div class="user-auth-status guest"><i class="fa-solid fa-clock"></i> Khách 5p: <span class="timer-count" id="guestCountdown">${formatTime(remaining)}</span></div>`;
  }

  badgeWrapper.innerHTML = `
    ${badgeContent}
    <button class="btn-admin-header" onclick="promptAdminLogin()" title="Trang Quản Trị Admin">
      <i class="fa-solid fa-user-gear"></i> Admin
    </button>
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }
}

function handleLogout() {
  localStorage.setItem('lms_user_logged_out', 'true');
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  localStorage.removeItem('lms_is_admin');
  localStorage.removeItem(ACTIVATED_KEY_STORAGE);
  localStorage.removeItem('lms_guest_expired');
  if (guestInterval) clearInterval(guestInterval);
  window.location.href = 'login.html';
}

function startGuestTimer() {
  if (guestInterval) clearInterval(guestInterval);

  updateGuestCountdownDisplay();

  guestInterval = setInterval(() => {
    let remaining = getGuestTimeRemaining();
    remaining--;

    if (remaining <= 0) {
      clearInterval(guestInterval);
      localStorage.setItem(GUEST_TIMER_KEY, '0');
      localStorage.removeItem(AUTH_KEY);
      localStorage.setItem('lms_guest_expired', 'true');
      window.location.href = 'login.html';
    } else {
      localStorage.setItem(GUEST_TIMER_KEY, remaining.toString());
      updateGuestCountdownDisplay(remaining);
    }
  }, 1000);
}

function restrictGuestPage() {
  if (window.location.pathname.includes('meo_hoc.html')) {
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');

    // Add Lock Icons to Tabs 2, 3, 4, 5
    tabItems.forEach((tab, index) => {
      if (index > 0) {
        const span = tab.querySelector('span');
        if (span && !span.innerHTML.includes('🔒')) {
          span.innerHTML = `🔒 ` + span.innerHTML;
        }
      }
    });

    // Replace contents of locked tabs with Lock Banner
    tabContents.forEach((content, index) => {
      if (index > 0) {
        content.innerHTML = `
          <div class="locked-tab-banner">
            <div class="locked-icon"><i class="fa-solid fa-lock"></i></div>
            <h3>TÍNH NĂNG BỊ KHÓA DÀNH CHO KHÁCH</h3>
            <p>Trang Mẹo Học phần này chỉ dành riêng cho <strong>Tài khoản VIP đã kích hoạt</strong>.<br>Vui lòng nhập Mã VIP 1 thiết bị để mở khóa trọn bộ!</p>
            <button class="btn-unlock-vip" onclick="showLoginModal()"><i class="fa-solid fa-key"></i> Đăng nhập / Kích hoạt Mã VIP</button>
          </div>
        `;
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', initAuthSystem);
