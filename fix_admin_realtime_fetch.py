with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace openAdminPanelModal with async fetch version
old_admin_modal = """function openAdminPanelModal() {
  trackCurrentDeviceUser();

  let modal = document.getElementById('adminModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'login-overlay';
    document.body.appendChild(modal);
  }

  const keys = getVipKeysDB();
  const users = getUsersDB();"""

new_admin_modal = """async function openAdminPanelModal() {
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

code = code.replace(old_admin_modal, new_admin_modal)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated openAdminPanelModal to fetch real-time Cloud DB data.")
