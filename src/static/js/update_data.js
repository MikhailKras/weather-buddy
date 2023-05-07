const changeDataForm = document.getElementById('change-data-form');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');

changeDataForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const userData = {
    username: changeDataForm.elements.username.value,
    email: changeDataForm.elements.email.value,
    city: changeDataForm.elements.city.value
  };

  fetch('/users/settings/update_data', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
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
    successMessage.textContent = 'Data changed successfully!';
    errorMessage.style.display = 'none';
    setTimeout(() => {
      window.location.href = '/users/me';
    }, 2000);
  })
  .catch((error) => {
    errorMessage.textContent = error.message;
    errorMessage.style.display = 'block';
  });
});
