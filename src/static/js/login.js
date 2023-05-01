const loginForm = document.getElementById('login-form');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const username = loginForm.elements.username.value;
  const password = loginForm.elements.password.value;

  fetch('/users/token', {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'password',
      username: username,
      password: password,
    }),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
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
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('token_type', data.token_type);
      successMessage.style.display = 'block';
      successMessage.textContent = 'Successfully logged in!';
      errorMessage.style.display = 'none';
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = 'block';
    });
});
