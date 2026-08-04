with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

# Update startGuestTimer to redirect to login.html on expiration
old_timer = """    if (remaining <= 0) {
      clearInterval(guestInterval);
      localStorage.setItem(GUEST_TIMER_KEY, '0');
      localStorage.removeItem(AUTH_KEY);
      showLoginModal(true);
    }"""

new_timer = """    if (remaining <= 0) {
      clearInterval(guestInterval);
      localStorage.setItem(GUEST_TIMER_KEY, '0');
      localStorage.removeItem(AUTH_KEY);
      localStorage.setItem('lms_guest_expired', 'true');
      window.location.href = 'login.html';
    }"""

acode = acode.replace(old_timer, new_timer)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js guest timer expiration logic.")

with open('login.html', 'r', encoding='utf-8') as f:
    lcode = f.read()

# Add expired banner check in login.html
old_DOMContentLoaded = "document.addEventListener('DOMContentLoaded', () => {"

new_DOMContentLoaded = """document.addEventListener('DOMContentLoaded', () => {
      // Check if redirected due to 5-minute guest timer expiration
      if (localStorage.getItem('lms_guest_expired') === 'true') {
        const errBox = document.getElementById('standaloneError');
        if (errBox) {
          errBox.innerHTML = '⚠️ <strong>HẾT THỜI GIAN 5 PHÚT DÙNG THỬ CHO KHÁCH!</strong><br>Vui lòng nhập Mã VIP để tiếp tục sử dụng hệ thống.';
          errBox.style.display = 'block';
        }
      }"""

lcode = lcode.replace(old_DOMContentLoaded, new_DOMContentLoaded)

with open('login.html', 'w', encoding='utf-8') as f:
    f.write(lcode)

print("Updated login.html to display guest expiration banner.")

