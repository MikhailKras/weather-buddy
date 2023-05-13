const form = document.getElementById('user-info-form');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message')

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = form.elements.username.value;
    const email = form.elements.email.value;
    const password = form.elements.password.value;
    const city = form.elements.city.value;

    errorMessage.style.display = "none";

    try {
        const response = await fetch('/users/register/details', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
            })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(`${data.detail}`);
        } else {
            errorMessage.style.display = 'none'
            successMessage.style.display = 'block'
            successMessage.textContent = data.message
            setTimeout(() => {
                window.location.href = '/users/login';
              }, 2000);
        }
    } catch (error) {
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
    }
});