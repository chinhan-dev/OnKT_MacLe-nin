import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Make promptAdminLogin navigate directly to admin.html
new_prompt_admin = """function promptAdminLogin() {
  window.location.href = 'admin.html';
}"""

pattern_prompt = r"function promptAdminLogin\(\) \{.*?\n\}"
code = re.sub(pattern_prompt, new_prompt_admin.strip(), code, flags=re.DOTALL)

# Update refreshAdminUI helper to re-render standalone page if on admin.html
helper_refresh = """async function refreshAdminUI() {
  if (window.location.pathname.endsWith('admin.html') && typeof renderAdminStandalonePage === 'function') {
    await renderAdminStandalonePage();
  } else if (typeof openAdminPanelModal === 'function') {
    await openAdminPanelModal();
  }
}"""

if 'refreshAdminUI' not in code:
    code = helper_refresh + "\n" + code

code = code.replace("await openAdminPanelModal();", "await refreshAdminUI();")
code = code.replace("openAdminPanelModal();", "refreshAdminUI();")

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated admin.js for standalone admin.html navigation.")
