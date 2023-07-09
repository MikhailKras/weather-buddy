const loginForm = document.getElementById("login-form");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");
const spinner = document.querySelector(".spinner-border");
const submitButton = document.getElementById("submit-button");

submitButton.addEventListener("click", () => {
  const username = loginForm.elements.username.value;
  const password = loginForm.elements.password.value;

  if (username.trim() === "" || password.trim() === "") {
    return;
  }

  spinner.style.display = "inline-block";
});

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const username = loginForm.elements.username.value;
  const password = loginForm.elements.password.value;

  if (username.trim() === "" || password.trim() === "") {
    return;
  }

  errorMessage.style.display = "none";

  fetch("/users/token", {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "password",
      username: username,
      password: password,
    }),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
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
      successMessage.style.display = "block";
      successMessage.textContent = "Successfully logged in!";
      errorMessage.style.display = "none";
      setTimeout(() => {
        window.location.href = "/users/me";
      }, 2000);
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    })
    .finally(() => {
      spinner.style.display = "none";
    });
});
