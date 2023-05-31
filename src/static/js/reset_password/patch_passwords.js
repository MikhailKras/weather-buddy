const resetPasswordForm = document.getElementById('reset-password-form');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');

resetPasswordForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const password_reset = {
    password: resetPasswordForm.elements['new_password'].value,
    password_confirm: resetPasswordForm.elements['confirm_password'].value,
  };

  errorMessage.style.display = "none";

  fetch('/users/password-reset/update', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(password_reset)
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      return response.json();
    })
    .then((data) => {
      successMessage.style.display = 'block';
      successMessage.textContent = data.message;
      errorMessage.style.display = 'none';
      setTimeout(() => {
        window.location.href = '/users/login';
      }, 2000);
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = 'block';
    });
});
