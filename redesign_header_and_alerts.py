import re

# 1. Update styles.css for ultra-sleek user badge capsule & custom toast dialogs
custom_ui_css = """

/* Sleek Integrated User Capsule in Header */
.user-auth-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-left: 6px;
}

.user-capsule {
  display: inline-flex;
  align-items: center;
  padding: 4px 6px 4px 14px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 800;
  white-space: nowrap !important;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.user-capsule.vip {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.user-capsule.guest {
  background-color: #fff7ed;
  color: #c2410c;
  border: 1px solid #ffedd5;
}

.capsule-divider {
  width: 1px;
  height: 14px;
  background-color: rgba(0, 0, 0, 0.15);
  margin: 0 8px;
}

.btn-logout-icon {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-logout-icon:hover {
  background-color: #fef2f2;
  transform: scale(1.15);
}

/* Custom Modern Toast Notification System */
.custom-toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.custom-toast {
  pointer-events: auto;
  min-width: 300px;
  max-width: 420px;
  padding: 14px 20px;
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  animation: toastSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  transition: all 0.3s ease;
}

.custom-toast.success {
  border-left: 5px solid #10b981;
}

.custom-toast.success .toast-icon {
  color: #10b981;
  background-color: #ecfdf5;
}

.custom-toast.error {
  border-left: 5px solid #ef4444;
}

.custom-toast.error .toast-icon {
  color: #ef4444;
  background-color: #fef2f2;
}

.custom-toast.info {
  border-left: 5px solid #2563eb;
}

.custom-toast.info .toast-icon {
  color: #2563eb;
  background-color: #eff6ff;
}

.toast-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  line-height: 1.4;
}

@keyframes toastSlideIn {
  from { transform: translateX(100%) scale(0.9); opacity: 0; }
  to { transform: translateX(0) scale(1); opacity: 1; }
}

/* Custom Modal Confirm Box */
.confirm-modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  z-index: 10001;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}

.confirm-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 28px 24px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  animation: modalScale 0.25s ease-out;
}

.confirm-card h3 {
  font-size: 1.15rem;
  color: #1e293b;
  margin-bottom: 8px;
}

.confirm-card p {
  font-size: 0.88rem;
  color: #64748b;
  margin-bottom: 20px;
}

.confirm-btns {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-confirm-yes {
  padding: 10px 20px;
  border-radius: 10px;
  background-color: #ef4444;
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-no {
  padding: 10px 20px;
  border-radius: 10px;
  background-color: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  font-weight: 700;
  cursor: pointer;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(custom_ui_css)

print("Added custom toast and confirm modal CSS to styles.css.")

