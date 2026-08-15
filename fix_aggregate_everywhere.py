import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

helper_code = """
function aggregateUsersFromKeys(keys, users) {
  const mergedUsers = [...users];
  for (const k of keys) {
    if (k.status === 'used' && k.deviceId) {
      let uObj = mergedUsers.find(u => u.deviceId === k.deviceId);
      if (!uObj) {
        mergedUsers.push({
          deviceId: k.deviceId,
          name: `Học viên ${k.deviceId}`,
          role: 'vip',
          activatedKey: k.key,
          deviceType: k.deviceId.includes('IPHO') || k.deviceId.includes('MOBI') ? '📱 Điện thoại' : '💻 Thiết bị',
          createdAt: k.activatedAt || k.createdAt || 'Đã dùng mã',
          lastActive: k.activatedAt || 'Đã dùng mã'
        });
      } else {
        uObj.role = 'vip';
        uObj.activatedKey = k.key;
      }
    }
  }
  return mergedUsers;
}
"""

new_cloud_system = """
const CLOUD_DB_ENDPOINT = 'https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde';

function aggregateUsersFromKeys(keys, users) {
  const mergedUsers = [...users];
  for (const k of keys) {
    if (k.status === 'used' && k.deviceId) {
      let uObj = mergedUsers.find(u => u.deviceId === k.deviceId);
      if (!uObj) {
        mergedUsers.push({
          deviceId: k.deviceId,
          name: `Học viên ${k.deviceId}`,
          role: 'vip',
          activatedKey: k.key,
          deviceType: k.deviceId.includes('IPHO') || k.deviceId.includes('MOBI') ? '📱 Điện thoại' : '💻 Thiết bị',
          createdAt: k.activatedAt || k.createdAt || 'Đã dùng mã',
          lastActive: k.activatedAt || 'Đã dùng mã'
        });
      } else {
        uObj.role = 'vip';
        uObj.activatedKey = k.key;
      }
    }
  }
  return mergedUsers;
}

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

        // Merge Users
        const localUsersData = localStorage.getItem(USERS_DB_STORAGE);
        let localUsers = localUsersData ? JSON.parse(localUsersData) : [];
        let mergedUsers = [...cloudUsers];
        for (const lu of localUsers) {
          const idx = mergedUsers.findIndex(cu => cu.deviceId === lu.deviceId);
          if (idx >= 0) {
            mergedUsers[idx] = lu;
          } else {
            mergedUsers.push(lu);
          }
        }

        // Auto-aggregate
        mergedUsers = aggregateUsersFromKeys(mergedKeys, mergedUsers);

        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
        localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

        return { keys: mergedKeys, users: mergedUsers };
      }
    }
  } catch (e) {
    console.warn('Cloud DB fetch offline, using local storage.', e);
  }

  const lKeys = getVipKeysDB();
  const lUsers = aggregateUsersFromKeys(lKeys, getUsersDB());
  return { keys: lKeys, users: lUsers };
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

    let mergedUsers = [...cloudUsers];
    for (const u of (usersToPush || getUsersDB())) {
      const idx = mergedUsers.findIndex(cu => cu.deviceId === u.deviceId);
      if (idx >= 0) mergedUsers[idx] = u; else mergedUsers.push(u);
    }

    // Auto-aggregate
    mergedUsers = aggregateUsersFromKeys(mergedKeys, mergedUsers);

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
"""

pattern = r"const CLOUD_DB_ENDPOINT = .*?async function pushCloudKeysDB\(keysToPush\) \{.*?\n\}"
code = re.sub(pattern, new_cloud_system.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with universal aggregateUsersFromKeys in both fetch and push.")
