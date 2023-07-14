document.addEventListener("DOMContentLoaded", () => {
  const errorMessage = document.getElementById("error-message");
  const errorMessageCity = document.getElementById("error-message-city");
  const errorMessagePassword = document.getElementById(
    "error-message-password"
  );

  const tabLinks = document.querySelectorAll(".nav-link");

  const hideErrorMessages = () => {
    errorMessage.style.display = "none";
    errorMessageCity.style.display = "none";
    errorMessagePassword.style.display = "none";
  };
  tabLinks.forEach((tab) => {
    tab.addEventListener("click", hideErrorMessages);
  });
});

const changeDataForm = document.getElementById("change-data-form");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");
const spinner = document.querySelector(
  "#submit-button-username-email .spinner-border"
);

changeDataForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const userData = {
    username: changeDataForm.elements.username.value,
    email: changeDataForm.elements.email.value,
  };

  errorMessage.style.display = "none";
  spinner.style.display = "inline-block";

  fetch("/users/settings/update_data", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
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
      successMessage.style.display = "none";
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    })
    .finally(() => {
      spinner.style.display = "none";
    });
});

const changeCityForm = document.getElementById("change-city-data-form");
const errorMessageCity = document.getElementById("error-message-city");
const successMessageCity = document.getElementById("success-message-city");
const spinner_city = document.querySelector(
  "#submit-button-city .spinner-border"
);
changeCityForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const cityInput = changeCityForm.elements.city.value;
  spinner_city.style.display = "inline-block";

  fetch(
    `/users/settings/city/choose_city_name?city_input=${encodeURIComponent(
      cityInput
    )}`
  )
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      window.location.href = `/users/settings/city/choose_city_name?city_input=${encodeURIComponent(
        cityInput
      )}`;
    })
    .catch((error) => {
      errorMessageCity.textContent = error.message;
      errorMessageCity.style.display = "block";
    })
    .finally(() => {
      spinner_city.style.display = "none";
    });
});

const changePasswordForm = document.getElementById("change-password-form");
const errorMessagePassword = document.getElementById("error-message-password");
const successMessagePassword = document.getElementById(
  "success-message-password"
);
const spinner_password = document.querySelector(
  "#submit-button-password .spinner-border"
);

changePasswordForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const passwords = {
    current_password: changePasswordForm.elements["current-password"].value,
    new_password: changePasswordForm.elements["new-password"].value,
    repeat_password: changePasswordForm.elements["repeat-password"].value,
  };

  errorMessagePassword.style.display = "none";
  spinner_password.style.display = "inline-block";

  fetch("/users/settings/change_password", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(passwords),
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
      successMessagePassword.style.display = "block";
      successMessagePassword.textContent = data.message;
      errorMessagePassword.style.display = "none";
      setTimeout(() => {
        window.location.href = "/users/me";
      }, 2000);
    })
    .catch((error) => {
      errorMessagePassword.textContent = error.message;
      errorMessagePassword.style.display = "block";
    })
    .finally(() => {
      spinner_password.style.display = "none";
    });
});

const deleteBtn = document.getElementById("delete-btn");
const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
const confirmationInput = document.getElementById("confirmation-input");
const spinner_delete = document.querySelector(
  "#confirm-delete-btn .spinner-border"
);

deleteBtn.addEventListener("click", () => {
  // Clear the confirmation input field when the modal is opened
  confirmationInput.value = "";
});

confirmDeleteBtn.addEventListener("click", async () => {
  const confirmation = confirmationInput.value.trim();

  if (confirmation !== "DELETE") {
    alert('Please enter the word "DELETE" to confirm the account deletion.');
    return;
  }

  spinner_delete.style.display = "inline-block";

  const response = await fetch("/users/settings/delete_user", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      // Optional body payload
    }),
  });

  if (response.ok) {
    setTimeout(() => {
      window.location.href = "/users/login";
    }, 2000);
  } else {
    // Handle error response
    console.error(`Error deleting account: ${response.statusText}`);
  }

  spinner_delete.style.display = "none";
});

// Prevent form submission on Enter key press
confirmationInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    confirmDeleteBtn.click();
  }
});
