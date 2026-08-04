import re

# 1. Upgrade handleVipSubmit in auth.js with try-catch-finally and 5s timeout
with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

new_handle_vip = """  async function handleVipSubmit() {
    const entered = passInput.value.trim();
    if (!entered) return;

    if (entered === 'chinhanxt') {
      setUserRole('vip');
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
  }"""

pattern_handle = r"async function handleVipSubmit\(\) \{.*?\n  \}"
acode = re.sub(pattern_handle, new_handle_vip.strip(), acode, flags=re.DOTALL)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js with try-catch-finally and 5s timeout.")

# 2. Upgrade fetchCloudData in admin.js with 3.5s timeout
with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

new_fetch_cloud = """async function fetchCloudData() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store', signal: controller.signal });
    clearTimeout(timer);

    if (res.ok) {
      const json = await res.json();
      if (json) {
        const dbObj = json.data || json;
        const cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        const cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];

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
    console.warn('Cloud DB fetch offline/timeout, using local storage.', e);
  }

  const lKeys = getVipKeysDB();
  const lUsers = aggregateUsersFromKeys(lKeys, getUsersDB());
  return { keys: lKeys, users: lUsers };
}"""

pattern_fetch = r"async function fetchCloudData\(\) \{.*?\n\}"
code = re.sub(pattern_fetch, new_fetch_cloud.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js fetchCloudData with AbortController 3.5s timeout.")
