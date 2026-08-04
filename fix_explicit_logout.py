with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

# Update initAuthSystem to check lms_user_logged_out flag
old_init = """async function initAuthSystem() {
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
          localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');
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
}"""

new_init = """async function initAuthSystem() {
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
}"""

acode = acode.replace(old_init, new_init)

# Update handleLogout to set lms_user_logged_out
old_logout = """function handleLogout() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  localStorage.removeItem('lms_is_admin');
  localStorage.removeItem(ACTIVATED_KEY_STORAGE);
  if (guestInterval) clearInterval(guestInterval);
  location.reload();
}"""

new_logout = """function handleLogout() {
  localStorage.setItem('lms_user_logged_out', 'true');
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(GUEST_TIMER_KEY);
  localStorage.removeItem('lms_is_admin');
  localStorage.removeItem(ACTIVATED_KEY_STORAGE);
  if (guestInterval) clearInterval(guestInterval);
  location.reload();
}"""

acode = acode.replace(old_logout, new_logout)

# Update setUserRole to clear lms_user_logged_out when logging in
old_set_role = """function setUserRole(role) {
  localStorage.setItem(AUTH_KEY, role);"""

new_set_role = """function setUserRole(role) {
  localStorage.removeItem('lms_user_logged_out');
  localStorage.setItem(AUTH_KEY, role);"""

acode = acode.replace(old_set_role, new_set_role)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js with explicit lms_user_logged_out flag.")
