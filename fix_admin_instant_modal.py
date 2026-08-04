with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Update openAdminPanelModal to show modal instantly with loading state
old_open_admin = """async function openAdminPanelModal() {
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

new_open_admin = """async function openAdminPanelModal() {
  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  // Render initial loading UI instantly!
  modal.innerHTML = `
    <div class="login-card admin-card" style="text-align: center; padding: 48px 32px;">
      <div class="login-logo" style="background: linear-gradient(135deg, #7c3aed, #4c1d95);"><i class="fa-solid fa-spinner fa-spin"></i></div>
      <h3 style="font-size: 1.2rem; color: #581c87; margin-top: 12px;">Đang tải Dashboard Admin...</h3>
      <p style="font-size: 0.88rem; color: #64748b;">Đang kết nối & đồng bộ dữ liệu Real-time từ Cloud DB</p>
    </div>
  `;
  modal.style.display = 'flex';

  // Fetch real-time Cloud Data asynchronously
  const cloudData = typeof fetchCloudData === 'function' ? await fetchCloudData() : { keys: getVipKeysDB(), users: getUsersDB() };
  const keys = cloudData.keys;
  const users = cloudData.users;"""

code = code.replace(old_open_admin, new_open_admin)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated openAdminPanelModal to show modal instantly with loading UI.")
