import re

# Add Auth CSS to styles.css
auth_css = """

/* ==========================================================================
   AUTHENTICATION & GUEST TIMER STYLES
   ========================================================================== */
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background-color: #ffffff;
  border-radius: 20px;
  border: 1px solid #cbd5e1;
  width: 100%;
  max-width: 480px;
  padding: 32px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 24px;
  text-align: center;
  animation: modalScale 0.3s ease-out;
}

@keyframes modalScale {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.login-logo {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px auto;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.login-header h2 {
  font-size: 1.4rem;
  font-weight: 800;
  color: #1e3a8a;
  margin-bottom: 4px;
}

.login-header p {
  font-size: 0.9rem;
  color: #64748b;
}

.login-options {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.btn-login-vip, .btn-login-guest {
  width: 100%;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s ease;

}

.btn-login-vip {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn-login-vip:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

.btn-login-guest {
  background-color: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.btn-login-guest:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}

.pass-input-group {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.pass-input-group input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #2563eb;
  font-size: 0.95rem;
  outline: none;
  font-weight: 600;
}

.pass-input-group button {
  padding: 12px 18px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.pass-error {
  color: #dc2626;
  font-size: 0.85rem;
  font-weight: 700;
  margin-top: 6px;
}

/* User Badge in Header */
.user-auth-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
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
  font-size: 0.95rem;
  background-color: #ffebd5;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Locked Tab Overlay on meo_hoc.html */
.locked-tab-banner {
  background-color: #ffffff;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  max-width: 600px;
  margin: 40px auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

.locked-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #fef2f2;
  color: #ef4444;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.locked-tab-banner h3 {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1e3a8a;
}

.locked-tab-banner p {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.5;
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
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(auth_css)

print("Auth CSS appended to styles.css.")
