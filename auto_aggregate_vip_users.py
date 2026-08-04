import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Enhance fetchCloudData to automatically aggregate users from used VIP keys
new_fetch_data = """async function fetchCloudData() {
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
        const mergedUsers = [...cloudUsers];
        for (const lu of localUsers) {
          const idx = mergedUsers.findIndex(cu => cu.deviceId === lu.deviceId);
          if (idx >= 0) {
            mergedUsers[idx] = lu;
          } else {
            mergedUsers.push(lu);
          }
        }

        // AUTO-AGGREGATE: Ensure every device that used a VIP key is listed as a VIP User
        for (const k of mergedKeys) {
          if (k.status === 'used' && k.deviceId) {
            let uObj = mergedUsers.find(u => u.deviceId === k.deviceId);
            if (!uObj) {
              mergedUsers.push({
                deviceId: k.deviceId,
                name: `Học viên ${k.deviceId}`,
                role: 'vip',
                activatedKey: k.key,
                deviceType: '📱/💻 Thiết bị',
                createdAt: k.activatedAt || k.createdAt || 'Đã dùng mã',
                lastActive: k.activatedAt || 'Đã dùng mã'
              });
            } else {
              uObj.role = 'vip';
              uObj.activatedKey = k.key;
            }
          }
        }

        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
        localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(mergedUsers));

        return { keys: mergedKeys, users: mergedUsers };
      }
    }
  } catch (e) {
    console.warn('Cloud DB fetch offline, using local storage.', e);
  }

  // Local fallback with auto-aggregation
  const lKeys = getVipKeysDB();
  const lUsers = getUsersDB();
  for (const k of lKeys) {
    if (k.status === 'used' && k.deviceId) {
      let uObj = lUsers.find(u => u.deviceId === k.deviceId);
      if (!uObj) {
        lUsers.push({
          deviceId: k.deviceId,
          name: `Học viên ${k.deviceId}`,
          role: 'vip',
          activatedKey: k.key,
          deviceType: '📱/💻 Thiết bị',
          createdAt: k.activatedAt || k.createdAt || 'Đã dùng mã',
          lastActive: k.activatedAt || 'Đã dùng mã'
        });
      } else {
        uObj.role = 'vip';
        uObj.activatedKey = k.key;
      }
    }
  }
  return { keys: lKeys, users: lUsers };
}"""

pattern = r"async function fetchCloudData\(\) \{.*?\n\}"
code = re.sub(pattern, new_fetch_data.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with automatic VIP user aggregation from used keys.")
