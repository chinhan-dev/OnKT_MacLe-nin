import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Add saveAndPushCloudData function
save_push_func = """
// Save & Overwrite Cloud DB Directly for Delete & Modify Actions
async function saveAndPushCloudData(keys, users) {
  localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keys));
  localStorage.setItem(USERS_DB_STORAGE, JSON.stringify(users));

  try {
    const putRes = await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keys: keys,
        users: users
      })
    });

    if (putRes.ok) {
      await putRes.json();
      console.log('Cloud DB save confirmed.');
    }
  } catch (e) {
    console.warn('Cloud DB save error:', e);
  }
}
"""

if 'saveAndPushCloudData' not in code:
    code = save_push_func + "\n" + code

# Update deleteVipKey
new_del_key = """function deleteVipKey(key) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Mã VIP', `Bạn có chắc chắn muốn xóa mã VIP <strong>${key}</strong> khỏi hệ thống?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys.filter(k => k.key.toUpperCase() !== key.toUpperCase());
      let users = cloudData.users;
      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa mã VIP ${key}`, 'info');
      await openAdminPanelModal();
    });
  }
}"""

pattern_del_key = r"function deleteVipKey\(key\) \{.*?\n\}"
code = re.sub(pattern_del_key, new_del_key.strip(), code, flags=re.DOTALL)

# Update deleteUserRecord
new_del_user = """function deleteUserRecord(devId) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Học Viên', `Bạn có chắc chắn muốn xóa dữ liệu học viên <strong>${devId}</strong>?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys;
      let users = cloudData.users.filter(u => u.deviceId !== devId);
      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa học viên ${devId}`, 'info');
      await openAdminPanelModal();
    });
  }
}"""

pattern_del_user = r"function deleteUserRecord\(devId\) \{.*?\n\}"
code = re.sub(pattern_del_user, new_del_user.strip(), code, flags=re.DOTALL)

# Update promoteUserToVip and demoteUserToGuest
new_promote = """async function promoteUserToVip(devId) {
  let cloudData = await fetchCloudData();
  let users = cloudData.users;
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = 'ADMIN_GRANTED';
    await saveAndPushCloudData(cloudData.keys, users);
    if (devId === getDeviceId()) {
      setUserRole('vip');
      location.reload();
    } else {
      await openAdminPanelModal();
    }
  }
}

async function demoteUserToGuest(devId) {
  let cloudData = await fetchCloudData();
  let users = cloudData.users;
  let u = users.find(x => x.deviceId === devId);
  if (u) {
    u.role = 'guest';
    u.activatedKey = 'N/A';
    await saveAndPushCloudData(cloudData.keys, users);
    if (devId === getDeviceId()) {
      setUserRole('guest');
      location.reload();
    } else {
      await openAdminPanelModal();
    }
  }
}"""

pattern_promote = r"async function promoteUserToVip\(devId\) \{.*?\nasync function demoteUserToGuest\(devId\) \{.*?\n\}"
code = re.sub(pattern_promote, new_promote.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with robust delete and promote/demote Cloud DB operations.")
