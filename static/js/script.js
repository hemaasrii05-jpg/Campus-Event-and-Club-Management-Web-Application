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
