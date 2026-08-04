with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace data parsing in fetchCloudData and pushCloudData
old_fetch_check = """      if (json && json.data) {
        const cloudKeys = json.data.keys || [];
        const cloudUsers = json.data.users || [];"""

new_fetch_check = """      if (json) {
        const dbObj = json.data || json;
        const cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        const cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];"""

code = code.replace(old_fetch_check, new_fetch_check)

old_push_check = """      if (json && json.data) {
        cloudKeys = json.data.keys || [];
        cloudUsers = json.data.users || [];
      }"""

new_push_check = """      if (json) {
        const dbObj = json.data || json;
        cloudKeys = Array.isArray(dbObj.keys) ? dbObj.keys : [];
        cloudUsers = Array.isArray(dbObj.users) ? dbObj.users : [];
      }"""

code = code.replace(old_push_check, new_push_check)

# Make generateNewVipKey async and await pushCloudKeysDB
old_gen_func = """function generateNewVipKey() {
  const code = 'MAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
  const keys = getVipKeysDB();
  keys.push({
    key: code,
    status: 'unused',
    deviceId: null,
    createdAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN')
  });
  pushCloudKeysDB(keys);
  return code;
}"""

new_gen_func = """async function generateNewVipKey() {
  const code = 'MAC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
  let keys = await fetchCloudKeysDB();
  keys.push({
    key: code,
    status: 'unused',
    deviceId: null,
    createdAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN')
  });
  await pushCloudKeysDB(keys);
  return code;
}"""

code = code.replace(old_gen_func, new_gen_func)

# Make "+ Tạo Mã VIP Mới" button listener await generateNewVipKey
old_gen_btn_listener = """  if (genBtn) genBtn.addEventListener('click', () => {
    const newCode = generateNewVipKey();
    if (typeof showToast === 'function') showToast(`🎉 Đã tạo Mã VIP mới: ${newCode}`, 'success'); else alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);
    openAdminPanelModal();
  });"""

new_gen_btn_listener = """  if (genBtn) genBtn.addEventListener('click', async () => {
    genBtn.disabled = true;
    genBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo mã...';
    const newCode = await generateNewVipKey();
    if (typeof showToast === 'function') showToast(`🎉 Đã tạo Mã VIP mới: ${newCode}`, 'success'); else alert(`🎉 Đã tạo Mã VIP mới: ${newCode}`);
    await openAdminPanelModal();
  });"""

code = code.replace(old_gen_btn_listener, new_gen_btn_listener)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js with robust JSONBlob parser & async key creation.")
