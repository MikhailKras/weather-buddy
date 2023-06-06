const resetPasswordForm = document.getElementById("reset-password-form");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");

resetPasswordForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const email = resetPasswordForm.elements.email.value;

  successMessage.style.display = "none";
  errorMessage.style.display = "none";

  fetch("/users/password-reset", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: email }),
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
      successMessage.style.display = "block";
      successMessage.textContent = data.message;
      errorMessage.style.display = "none";
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    });
});
