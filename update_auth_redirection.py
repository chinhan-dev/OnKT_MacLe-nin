import re

with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

new_init_auth = """async function initAuthSystem() {
  const isLoginPage = window.location.pathname.endsWith('login.html');
  const isLoggedOut = localStorage.getItem('lms_user_logged_out') === 'true';

  if (isLoggedOut) {
    if (!isLoginPage) {
      window.location.href = 'login.html';
    }
    return;
  }

  let role = getUserRole();

  // If user is Master Admin, always maintain access
  if (localStorage.getItem('lms_is_admin') === 'true') {
    applyRolePermissions('vip');
    if (isLoginPage) window.location.href = 'index.html';
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
    if (!isLoginPage) {
      window.location.href = 'login.html';
    }
  } else {
    if (isLoginPage) {
      window.location.href = 'index.html';
    } else {
      applyRolePermissions(role);
    }
  }
}"""

pattern_init = r"async function initAuthSystem\(\) \{.*?\n\}"
acode = re.sub(pattern_init, new_init_auth.strip(), acode, flags=re.DOTALL)

# Update handleLogout to redirect to login.html
new_logout = """function handleLogout() {
  localStorage.setItem('lms_user_logged_out', 'true');
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  localStorage.removeItem('lms_is_admin');
  localStorage.removeItem(ACTIVATED_KEY_STORAGE);
  if (guestInterval) clearInterval(guestInterval);
  window.location.href = 'login.html';
}"""

pattern_logout = r"function handleLogout\(\) \{.*?\n\}"
acode = re.sub(pattern_logout, new_logout.strip(), acode, flags=re.DOTALL)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js with clean login.html redirection.")

# Update admin.js so verifying Admin password redirects to index.html if on login.html
with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_verify = """    if (entered === ADMIN_PASS) {
      modal.style.display = 'none';
      localStorage.setItem('lms_is_admin', 'true');
      setUserRole('vip');
      openAdminPanelModal();
    }"""

new_verify = """    if (entered === ADMIN_PASS) {
      modal.style.display = 'none';
      localStorage.setItem('lms_is_admin', 'true');
      setUserRole('vip');
      if (window.location.pathname.endsWith('login.html')) {
        window.location.href = 'index.html?openAdmin=true';
      } else {
        openAdminPanelModal();
      }
    }"""

code = code.replace(old_verify, new_verify)

# Auto open admin modal if URL has ?openAdmin=true
auto_open_admin = """
document.addEventListener('DOMContentLoaded', () => {
  trackCurrentDeviceUser();
  if (window.location.search.includes('openAdmin=true')) {
    history.replaceState(null, '', window.location.pathname);
    openAdminPanelModal();
  }
});
"""

code = code.replace("document.addEventListener('DOMContentLoaded', trackCurrentDeviceUser);", auto_open_admin.strip())

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with ?openAdmin=true support.")
