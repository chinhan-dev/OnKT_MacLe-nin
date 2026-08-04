import re

CLOUD_DB_URL = "https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde"

# Update admin.js to sync with Cloud DB
with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

cloud_sync_code = """
const CLOUD_DB_ENDPOINT = 'https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde';

// Fetch Keys from Cloud DB asynchronously
async function fetchCloudKeysDB() {
  try {
    const res = await fetch(CLOUD_DB_ENDPOINT);
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.keys)) {
        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(json.data.keys));
        return json.data.keys;
      }
    }
  } catch (e) {
    console.warn('Cloud DB offline, using local storage.');
  }
  return getVipKeysDB();
}

// Push Keys to Cloud DB asynchronously
async function pushCloudKeysDB(keys) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
  try {
    const users = getUsersDB();
    await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'LMS_VIP_KEYS',
        data: { keys: keys, users: users }
      })
    });
  } catch (e) {
    console.warn('Failed to push to Cloud DB.');
  }
}
"""

if 'CLOUD_DB_ENDPOINT' not in code:
    code = cloud_sync_code + "\n" + code

# Update redeemVipKey to sync with Cloud DB
old_redeem = """function redeemVipKey(enteredKey) {"""
new_redeem = """async function redeemVipKeyAsync(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();
  let keys = await fetchCloudKeysDB();
  const currentDevId = getDeviceId();

  const keyObj = keys.find(k => k.key.toUpperCase() === cleanKey);

  if (!keyObj) {
    return { success: false, msg: '❌ Mã kích hoạt không tồn tại! Kiểm tra lại mã.' };
  }

  if (keyObj.status === 'used' && keyObj.deviceId !== currentDevId) {
    return { 
      success: false, 
      msg: `❌ Mã ${cleanKey} đã được kích hoạt trên máy khác (${keyObj.deviceId})!` 
    };
  }

  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');

  await pushCloudKeysDB(keys);

  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  setUserRole('vip');
  trackCurrentDeviceUser();
  return { success: true, msg: '🎉 Kích hoạt VIP thành công trên thiết bị này!' };
}

function redeemVipKey(enteredKey) {"""

code = code.replace(old_redeem, new_redeem)

# Update generateNewVipKey, deleteVipKey, promoteUserToVip, demoteUserToGuest, deleteUserRecord to call pushCloudKeysDB
code = code.replace("saveVipKeysDB(keys);", "pushCloudKeysDB(keys);")
code = code.replace("saveUsersDB(users);", "pushCloudKeysDB(getVipKeysDB());")

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with Cloud DB Real-time Sync.")

# Update auth.js to call redeemVipKeyAsync
with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

old_handle_vip = """  function handleVipSubmit() {
    const entered = passInput.value.trim();
    if (!entered) return;

    // Check if master admin pass entered directly
    if (entered === 'chinhanxt') {
      setUserRole('vip');
      modal.style.display = 'none';
      location.reload();
      return;
    }

    // Check device-bound VIP key
    const res = redeemVipKey(entered);
    if (res.success) {
      if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);
      modal.style.display = 'none';
      location.reload();
    } else {
      passErr.textContent = res.msg;
      passErr.style.display = 'block';
    }
  }"""

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
    submitPass.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

    const res = typeof redeemVipKeyAsync === 'function' 
      ? await redeemVipKeyAsync(entered) 
      : redeemVipKey(entered);

    submitPass.disabled = false;
    submitPass.innerHTML = '<i class="fa-solid fa-arrow-right"></i> Kích hoạt';

    if (res.success) {
      if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);
      modal.style.display = 'none';
      location.reload();
    } else {
      passErr.textContent = res.msg;
      passErr.style.display = 'block';
    }
  }"""

acode = acode.replace(old_handle_vip, new_handle_vip)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js to call Cloud DB async verification.")

