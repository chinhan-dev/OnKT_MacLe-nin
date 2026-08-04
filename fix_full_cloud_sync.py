import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

new_sync_system = """
const CLOUD_DB_ENDPOINT = 'https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde';

// Fetch Both Keys & Users from Cloud DB & Merge Cleanly
async function fetchCloudData() {
  try {
    const res = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store' });
    if (res.ok) {
      const json = await res.json();
      if (json && json.data) {
        const cloudKeys = json.data.keys || [];
        const cloudUsers = json.data.users || [];

        // Merge Keys
        const localKeysData = localStorage.getItem(VIP_KEYS_STORAGE);
        let localKeys = localKeysData ? JSON.parse(localKeysData) : [];
        const mergedKeys = [...cloudKeys];
        for (const lk of localKeys) {
          if (!mergedKeys.some(ck => ck.key.toUpperCase() === lk.key.toUpperCase())) {
            mergedKeys.push(lk);
          }
        }
        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));

        // Merge Users
        const localUsersData = localStorage.getItem(USERS_DB_STORAGE);
        let localUsers = localUsersData ? JSON.parse(localUsersData) : [];
        const mergedUsers = [...cloudUsers];
        for (const lu of localUsers) {
          const idx = mergedUsers.findIndex(cu => cu.deviceId === lu.deviceId);
          if (idx >= 0) {
            mergedUsers[idx] = lu;
          } else {
            mergedUsers.push(lu);
          }
        }
        localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

        return { keys: mergedKeys, users: mergedUsers };
      }
    }
  } catch (e) {
    console.warn('Cloud DB fetch offline, using local storage.', e);
  }
  return { keys: getVipKeysDB(), users: getUsersDB() };
}

// Alias for backward compatibility
async function fetchCloudKeysDB() {
  const d = await fetchCloudData();
  return d.keys;
}

// Push Both Keys & Users to Cloud DB Safely with Merge
async function pushCloudData(keysToPush, usersToPush) {
  try {
    const getRes = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store' });
    let cloudKeys = [];
    let cloudUsers = [];
    if (getRes.ok) {
      const json = await getRes.json();
      if (json && json.data) {
        cloudKeys = json.data.keys || [];
        cloudUsers = json.data.users || [];
      }
    }

    const mergedKeys = [...cloudKeys];
    for (const k of (keysToPush || getVipKeysDB())) {
      const idx = mergedKeys.findIndex(ck => ck.key.toUpperCase() === k.key.toUpperCase());
      if (idx >= 0) mergedKeys[idx] = k; else mergedKeys.push(k);
    }

    const mergedUsers = [...cloudUsers];
    for (const u of (usersToPush || getUsersDB())) {
      const idx = mergedUsers.findIndex(cu => cu.deviceId === u.deviceId);
      if (idx >= 0) mergedUsers[idx] = u; else mergedUsers.push(u);
    }

    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
    localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

    const putRes = await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'LMS_VIP_KEYS',
        data: { keys: mergedKeys, users: mergedUsers }
      })
    });

    if (putRes.ok) {
      await putRes.json();
    }
  } catch (e) {
    console.warn('Failed to push to Cloud DB:', e);
  }
}

// Alias for backward compatibility
async function pushCloudKeysDB(keysToPush) {
  await pushCloudData(keysToPush, getUsersDB());
}
"""

pattern = r"const CLOUD_DB_ENDPOINT = .*?async function pushCloudKeysDB\(keysToPush\) \{.*?\n\}"
code = re.sub(pattern, new_sync_system.strip(), code, flags=re.DOTALL)

# Update trackCurrentDeviceUser to sync user record to cloud
old_track = """function trackCurrentDeviceUser() {"""
new_track = """async function trackCurrentDeviceUser() {"""
code = code.replace(old_track, new_track)

# Add cloud push at end of trackCurrentDeviceUser
old_track_end = """  saveUsersDB(users);
}"""
new_track_end = """  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));
  await pushCloudData(getVipKeysDB(), users);
}"""
code = code.replace(old_track_end, new_track_end)

# Update openAdminPanelModal to use fetchCloudData()
old_open_admin = """async function openAdminPanelModal() {
  trackCurrentDeviceUser();

  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  // Fetch latest real-time data from Cloud DB
  const keys = typeof fetchCloudKeysDB === 'function' ? await fetchCloudKeysDB() : getVipKeysDB();
  const users = getUsersDB();"""

new_open_admin = """async function openAdminPanelModal() {
  await trackCurrentDeviceUser();

  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  // Fetch real-time Cloud Data for BOTH Keys & Users!
  const cloudData = typeof fetchCloudData === 'function' ? await fetchCloudData() : { keys: getVipKeysDB(), users: getUsersDB() };
  const keys = cloudData.keys;
  const users = cloudData.users;"""

code = code.replace(old_open_admin, new_open_admin)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with complete Keys & Users Cloud DB sync.")
