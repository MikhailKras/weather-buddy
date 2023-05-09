const changePasswordForm = document.getElementById('change-password-form');
const errorMessagePassword = document.getElementById('error-message-password');
const successMessagePassword = document.getElementById('success-message-password');

changePasswordForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const passwords = {
    current_password: changePasswordForm.elements['current-password'].value,
    repeat_password: changePasswordForm.elements['repeat-password'].value,
    new_password: changePasswordForm.elements['new-password'].value
  };

  fetch('/users/settings/change_password', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(passwords)
  })
  .then((response) => {
    if (!response.ok) {
      return response.json().then((data) => {
        throw new Error(data.detail);
      });
    }
    successMessagePassword.style.display = 'block';
    successMessagePassword.textContent = 'Password changed successfully!';
    errorMessagePassword.style.display = 'none';
    setTimeout(() => {
      window.location.href = '/users/me';
    }, 2000);
  })
  .catch((error) => {
    errorMessagePassword.textContent = error.message;
    errorMessagePassword.style.display = 'block';
  });
});
