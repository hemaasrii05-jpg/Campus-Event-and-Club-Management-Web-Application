document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-password').forEach((button) => {
    const targetId = button.getAttribute('data-target');
    const input = document.getElementById(targetId);

    if (!input) return;

    const showPassword = () => {
      input.type = 'text';
    };

    const hidePassword = () => {
      input.type = 'password';
    };

    button.addEventListener('mousedown', showPassword);
    button.addEventListener('mouseup', hidePassword);
    button.addEventListener('mouseleave', hidePassword);
    button.addEventListener('touchstart', showPassword, { passive: true });
    button.addEventListener('touchend', hidePassword);
    button.addEventListener('touchcancel', hidePassword);
  });
});

// UI helpers: modal confirm and toast
function showConfirm(message) {
  return new Promise((resolve) => {
    const modal = document.getElementById('confirm-modal');
    const msg = document.getElementById('confirm-modal-message');
    const ok = document.getElementById('confirm-ok');
    const cancel = document.getElementById('confirm-cancel');

    msg.textContent = message;
    modal.setAttribute('aria-hidden', 'false');

    function cleanup(result) {
      modal.setAttribute('aria-hidden', 'true');
      ok.removeEventListener('click', onOk);
      cancel.removeEventListener('click', onCancel);
      resolve(result);
    }

    function onOk() { cleanup(true); }
    function onCancel() { cleanup(false); }

    ok.addEventListener('click', onOk);
    cancel.addEventListener('click', onCancel);
  });
}

function showToast(message, type='success', ttl=3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = message;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; setTimeout(()=>t.remove(), 400); }, ttl);
}

window.ui = { showConfirm, showToast };
