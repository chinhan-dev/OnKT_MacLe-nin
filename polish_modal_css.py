with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the authentication section in styles.css with high-end polished styles
new_auth_css = """

/* ==========================================================================
   HIGH-END AUTHENTICATION & GUEST TIMER STYLES
   ========================================================================== */
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: #ffffff;
  border-radius: 24px;
  border: 1px solid #cbd5e1;
  width: 100%;
  max-width: 440px;
  padding: 36px 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 24px;
  text-align: center;
  animation: modalPop 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalPop {
  from { transform: scale(0.92) translateY(10px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.login-logo {
  width: 68px;
  height: 68px;
  border-radius: 20px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  font-size: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px auto;
  box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4);
}

.login-header h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #1e3a8a;
  margin-bottom: 6px;
  letter-spacing: -0.02em;
}

.login-header p {
  font-size: 0.88rem;
  color: #64748b;
  line-height: 1.5;
}

.login-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.btn-login-vip, .btn-login-guest {
  width: 100%;
  padding: 14px 20px;
  border-radius: 14px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-login-vip {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
}

.btn-login-vip:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

.btn-login-guest {
  background-color: #f8fafc;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.btn-login-guest:hover {
  background-color: #f1f5f9;
  color: #0f172a;
  border-color: #94a3b8;
}

.pass-input-group {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.pass-input-group input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid #2563eb;
  font-size: 0.92rem;
  outline: none;
  font-weight: 600;
  background-color: #ffffff;
  color: #0f172a;
}

.pass-input-group button {
  padding: 12px 18px;
  background-color: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pass-input-group button:hover {
  background-color: #1d4ed8;
}

.pass-error {
  color: #dc2626;
  font-size: 0.85rem;
  font-weight: 700;
  margin-top: 8px;
}

/* User Badge in Header */
.user-auth-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 800;
}

.user-auth-status.vip {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.user-auth-status.guest {
  background-color: #fff7ed;
  color: #c2410c;
  border: 1px solid #ffedd5;
}

.timer-count {
  font-family: monospace;
  font-size: 0.92rem;
  background-color: rgba(194, 65, 12, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
}

/* Locked Tab Banner on meo_hoc.html */
.locked-tab-banner {
  background-color: #ffffff;
  border: 2px dashed #cbd5e1;
  border-radius: 20px;
  padding: 48px 36px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  max-width: 560px;
  margin: 40px auto;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
}

.locked-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background-color: #fef2f2;
  color: #ef4444;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

.locked-tab-banner h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e3a8a;
  margin-top: 4px;
}

.locked-tab-banner p {
  font-size: 0.92rem;
  color: #64748b;
  line-height: 1.6;
}

.btn-unlock-vip {
  padding: 12px 24px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  border-radius: 9999px;
  border: none;
  font-weight: 800;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-unlock-vip:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}
"""

if "AUTHENTICATION & GUEST TIMER STYLES" in css:
    split_css = css.split("AUTHENTICATION & GUEST TIMER STYLES")[0]
    # Remove trailing /*
    if split_css.endswith("/* ==========================================================================\n   "):
        split_css = split_css[:-75]
    final_css = split_css + new_auth_css
else:
    final_css = css + new_auth_css

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(final_css)

print("Updated styles.css with high-end polished modal design.")
