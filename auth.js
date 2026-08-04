/* ==========================================================================
   AUTH & GUEST TIMER MANAGER (Secret VIP Pass)
   ========================================================================== */

const AUTH_KEY = 'lms_user_role';
const GUEST_TIMER_KEY = 'lms_guest_timer_secs';
const GUEST_MAX_TIME = 300; // 5 minutes in seconds

let guestInterval = null;

function getUserRole() {
  return localStorage.getItem(AUTH_KEY) || null;
}

function setUserRole(role) {
  localStorage.removeItem('lms_user_logged_out');
  localStorage.setItem(AUTH_KEY, role);
  if (role === 'guest') {
    if (!localStorage.getItem(GUEST_TIMER_KEY)) {
      localStorage.setItem(GUEST_TIMER_KEY, GUEST_MAX_TIME.toString());
    }
  } else {
    localStorage.removeItem(GUEST_TIMER_KEY);
  }
}

function getGuestTimeRemaining() {
  const val = localStorage.getItem(GUEST_TIMER_KEY);
  return val ? parseInt(val, 10) : GUEST_MAX_TIME;
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

async function initAuthSystem() {
  // If user explicitly clicked Logout, respect logout and show login modal!
  if (localStorage.getItem('lms_user_logged_out') === 'true') {
    showLoginModal();
    return;
  }

  let role = getUserRole();

  // If user is Master Admin, always maintain access
  if (localStorage.getItem('lms_is_admin') === 'true') {
    applyRolePermissions('vip');
    return;
  }

  // Check Cloud DB for device activation status
  if (typeof fetchCloudData === 'function') {
    try {
      const cloudData = await fetchCloudData();
      const devId = typeof getDeviceId === 'function' ? getDeviceId() : null;
      if (devId) {
        const u = cloudData.users.find(x => x.deviceId === devId);
        if (u && u.role === 'vip') {
          role = 'vip';
          setUserRole('vip');
        } else if (u && u.role === 'guest') {
          role = 'guest';
          setUserRole('guest');
        } else {
          // Device is not in Cloud DB as VIP -> revoke local VIP!
          if (role === 'vip') {
            localStorage.removeItem(AUTH_KEY);
            localStorage.removeItem(ACTIVATED_KEY_STORAGE);
            role = null;
          }
        }
      }
    } catch (e) {
      console.warn('Could not verify role with Cloud DB:', e);
    }
  }

  if (!role) {
    showLoginModal();
  } else {
    applyRolePermissions(role);
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
        ⚠️ HẾT THỜI GIAN 5 PHÚT THAO TÁC CHO KHÁCH!<br>Vui lòng nhập mật khẩu tài khoản VIP để tiếp tục sử dụng.
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
            <i class="fa-solid fa-key"></i> Đã Có Quyền (Nhập Mã VIP 1 Thiết Bị)
          </button>
          <div class="pass-input-group" id="passGroup" style="display: none;">
            <input type="text" id="vipPasswordInput" placeholder="Nhập mã VIP kích hoạt..." style="text-transform: uppercase;">
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
            <i class="fa-solid fa-user-gear"></i> Đăng nhập Admin Quản Lý Mã
          </button>
        </div>
      </div>
    </div>
  `;

  modal.style.display = 'flex';

  // Events
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

    if (entered === 'chinhanxt') {
      localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');
      modal.style.display = 'none';
      location.reload();
      return;
    }

    passErr.style.display = 'none';
    submitPass.disabled = true;
    submitPass.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Kích hoạt...';

    try {
      // 5-second max timeout limit
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
    badgeContent = `<div class="user-auth-status vip"><i class="fa-solid fa-circle-check"></i> Đã có quyền (VIP)</div>`;
  } else if (role === 'guest') {
    const remaining = getGuestTimeRemaining();
    badgeContent = `<div class="user-auth-status guest"><i class="fa-solid fa-clock"></i> Khách: <span class="timer-count" id="guestCountdown">${formatTime(remaining)}</span></div>`;
  }

  badgeWrapper.innerHTML = `
    ${badgeContent}
    <button class="btn-admin-header" onclick="promptAdminLogin()" title="Trang Quản Trị Admin ">
      <i class="fa-solid fa-user-gear"></i> Admin
    </button>
    <button class="btn-logout-header" id="logoutBtn" title="Đăng xuất khỏi hệ thống">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Đăng xuất</span>
    </button>
  `;

  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}

function handleLogout() {
  localStorage.setItem('lms_user_logged_out', 'true');
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  localStorage.removeItem('lms_is_admin');
  localStorage.removeItem(ACTIVATED_KEY_STORAGE);
  if (guestInterval) clearInterval(guestInterval);
  location.reload();
}

function startGuestTimer() {
  if (guestInterval) clearInterval(guestInterval);

  guestInterval = setInterval(() => {
    let remaining = getGuestTimeRemaining();
    remaining--;

    if (remaining <= 0) {
      clearInterval(guestInterval);
      localStorage.setItem(GUEST_TIMER_KEY, '0');
      localStorage.removeItem(AUTH_KEY);
      showLoginModal(true);
    } else {
      localStorage.setItem(GUEST_TIMER_KEY, remaining.toString());
      const el = document.getElementById('guestCountdown');
      if (el) el.textContent = formatTime(remaining);
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
            <p>Trang Mẹo Học phần này chỉ dành riêng cho <strong>Tài khoản đã có quyền</strong>.<br>Vui lòng đăng nhập với mật khẩu VIP để mở khóa trọn bộ!</p>
            <button class="btn-unlock-vip" onclick="showLoginModal()"><i class="fa-solid fa-key"></i> Đăng nhập Mật Khẩu VIP</button>
          </div>
        `;
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', initAuthSystem);
