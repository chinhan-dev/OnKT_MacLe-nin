/* ==========================================================================
   CUSTOM HIGH-END TOAST & CONFIRM DIALOG HELPER
   ========================================================================== */

function showToast(message, type = 'success') {
  let container = document.getElementById('customToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'customToastContainer';
    container.className = 'custom-toast-container';
    document.body.appendChild(container);
  }

  const iconMap = {
    success: 'fa-circle-check',
    error: 'fa-circle-exclamation',
    info: 'fa-circle-info'
  };

  const toast = document.createElement('div');
  toast.className = `custom-toast ${type}`;
  toast.innerHTML = `
    <div class="toast-icon"><i class="fa-solid ${iconMap[type] || 'fa-bell'}"></i></div>
    <div class="toast-message">${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function showConfirmModal(title, message, onConfirm) {
  let modal = document.getElementById('customConfirmModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'customConfirmModal';
    modal.className = 'confirm-modal-overlay';
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div class="confirm-card">
      <div style="width: 48px; height: 48px; border-radius: 50%; background: #fef2f2; color: #ef4444; font-size: 22px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto;">
        <i class="fa-solid fa-triangle-exclamation"></i>
      </div>
      <h3>${title}</h3>
      <p>${message}</p>
      <div class="confirm-btns">
        <button class="btn-confirm-no" id="btnConfirmNo">Hủy bỏ</button>
        <button class="btn-confirm-yes" id="btnConfirmYes">Xác nhận xóa</button>
      </div>
    </div>
  `;

  modal.style.display = 'flex';

  document.getElementById('btnConfirmNo').onclick = () => { modal.style.display = 'none'; };
  document.getElementById('btnConfirmYes').onclick = () => {
    modal.style.display = 'none';
    if (onConfirm) onConfirm();
  };
}
