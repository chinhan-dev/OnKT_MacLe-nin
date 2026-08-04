import re

with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

# Update initAuthSystem to verify role against Cloud DB
new_init_auth = """async function initAuthSystem() {
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

pattern_init = r"function initAuthSystem\(\) \{.*?\n\}"
acode = re.sub(pattern_init, new_init_auth.strip(), acode, flags=re.DOTALL)

# Update Master Admin login to set lms_is_admin flag
acode = acode.replace("setUserRole('vip');", "localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');")

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js with real-time Cloud DB role verification.")

# Update admin.js to clear lms_is_admin on normal logout if needed
with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("setUserRole('vip');", "localStorage.setItem('lms_is_admin', 'true'); setUserRole('vip');")

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js master admin flag.")
