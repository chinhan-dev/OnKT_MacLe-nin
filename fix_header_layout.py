import re

# 1. Update auth.js to append badge to end of controls/top-nav
with open('auth.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_func = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badgeWrapper = document.getElementById('userAuthWrapper');
  if (!badgeWrapper) {
    badgeWrapper = document.createElement('div');
    badgeWrapper.id = 'userAuthWrapper';
    badgeWrapper.style.display = 'inline-flex';
    badgeWrapper.style.alignItems = 'center';
    badgeWrapper.style.gap = '8px';
    controls.insertBefore(badgeWrapper, controls.firstChild);
  }"""

new_func = """function renderUserBadge(role) {
  let controls = document.querySelector('.controls') || document.querySelector('.top-nav');
  if (!controls) return;

  let badgeWrapper = document.getElementById('userAuthWrapper');
  if (!badgeWrapper) {
    badgeWrapper = document.createElement('div');
    badgeWrapper.id = 'userAuthWrapper';
    badgeWrapper.className = 'user-auth-wrapper';
    controls.appendChild(badgeWrapper);
  }"""

code = code.replace(old_func, new_func)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated auth.js to append badge to the end of header controls.")

# 2. Update styles.css with clean single-line header styles
with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

header_layout_css = """

/* Header User Auth Layout */
.user-auth-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
  border-left: 1px solid var(--border-color);
  padding-left: 14px;
}

.user-auth-status {
  white-space: nowrap !important;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 800;
  line-height: 1;
}

.btn-logout-header {
  white-space: nowrap !important;
  padding: 6px 14px;
  border-radius: 9999px;
  background-color: #fef2f2;
  color: #ef4444;
  border: 1px solid #fca5a5;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  line-height: 1;
}

.btn-logout-header:hover {
  background-color: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(header_layout_css)

print("Updated styles.css with clean single-line header layout.")

