import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Unified aggregateUsersFromKeys
new_aggregate = """function aggregateUsersFromKeys(keys, users) {
  const mergedUsers = [...users];

  // 1. Sync used keys to users
  for (const k of keys) {
    if (k.status === 'used' && k.deviceId) {
      let uObj = mergedUsers.find(u => u.deviceId === k.deviceId);
      if (uObj) {
        uObj.role = 'vip';
        uObj.activatedKey = k.key;
      }
    }
  }

  // 2. Sync user key activations to keys array
  for (const u of mergedUsers) {
    if (u.role === 'vip' && u.activatedKey && u.activatedKey.startsWith('MAC-')) {
      let kObj = keys.find(k => k.key.toUpperCase() === u.activatedKey.toUpperCase());
      if (kObj) {
        kObj.status = 'used';
        kObj.deviceId = u.deviceId;
      }
    }
  }

  return mergedUsers;
}"""

pattern_agg = r"function aggregateUsersFromKeys\(keys, users\) \{.*?\n\}"
code = re.sub(pattern_agg, new_aggregate.strip(), code, flags=re.DOTALL)

# Upgrade redeemVipKeyAsync
new_redeem_async = """async function redeemVipKeyAsync(enteredKey) {
  const cleanKey = enteredKey.trim().toUpperCase();
  let cloudData = await fetchCloudData();
  let keys = cloudData.keys;
  let users = cloudData.users;
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

  const nowStr = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');

  // Update Key
  keyObj.status = 'used';
  keyObj.deviceId = currentDevId;
  keyObj.activatedAt = nowStr;

  // Update User
  let u = users.find(x => x.deviceId === currentDevId);
  if (u) {
    u.role = 'vip';
    u.activatedKey = cleanKey;
    u.lastActive = nowStr;
  } else {
    users.push({
      deviceId: currentDevId,
      name: `Học viên ${currentDevId}`,
      role: 'vip',
      activatedKey: cleanKey,
      deviceType: currentDevId.includes('IPHO') || currentDevId.includes('MOBI') ? '📱 Điện thoại' : '💻 Thiết bị',
      createdAt: nowStr,
      lastActive: nowStr
    });
  }

  // Save both local & cloud
  setUserRole('vip');
  localStorage.setItem(ACTIVATED_KEY_STORAGE, cleanKey);
  await saveAndPushCloudData(keys, users);

  return { success: true, msg: `🎉 Kích hoạt VIP thành công với mã ${cleanKey}!` };
}"""

pattern_redeem = r"async function redeemVipKeyAsync\(enteredKey\) \{.*?\n\}"
code = re.sub(pattern_redeem, new_redeem_async.strip(), code, flags=re.DOTALL)

# Upgrade deleteVipKey
new_delete_key = """function deleteVipKey(key) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Mã VIP', `Bạn có chắc chắn muốn xóa mã VIP <strong>${key}</strong> khỏi hệ thống?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys.filter(k => k.key.toUpperCase() !== key.toUpperCase());
      let users = cloudData.users;

      // Demote any user that was using this deleted key
      for (let u of users) {
        if (u.activatedKey && u.activatedKey.toUpperCase() === key.toUpperCase()) {
          u.role = 'guest';
          u.activatedKey = 'N/A';
        }
      }

      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa mã VIP ${key}`, 'info');
      await openAdminPanelModal();
    });
  }
}"""

pattern_del_key = r"function deleteVipKey\(key\) \{.*?\n\}"
code = re.sub(pattern_del_key, new_delete_key.strip(), code, flags=re.DOTALL)

# Upgrade deleteUserRecord
new_delete_user = """function deleteUserRecord(devId) {
  if (typeof showConfirmModal === 'function') {
    showConfirmModal('Xóa Học Viên', `Bạn có chắc chắn muốn xóa dữ liệu học viên <strong>${devId}</strong>?`, async () => {
      let cloudData = await fetchCloudData();
      let keys = cloudData.keys;
      let users = cloudData.users.filter(u => u.deviceId !== devId);

      # Free up any VIP key bound to this deleted user
      for (let k of keys) {
        if (k.deviceId === devId) {
          k.status = 'unused';
          k.deviceId = null;
        }
      }

      await saveAndPushCloudData(keys, users);
      if (typeof showToast === 'function') showToast(`🗑️ Đã xóa học viên ${devId}`, 'info');
      await openAdminPanelModal();
    });
  }
}"""

pattern_del_user = r"function deleteUserRecord\(devId\) \{.*?\n\}"
code = re.sub(pattern_del_user, new_delete_user.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with bi-directional redemption and deletion sync.")
