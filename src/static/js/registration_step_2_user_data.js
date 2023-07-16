form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = form.elements.username.value;
  const email = form.elements.email.value;
  const password = form.elements.password.value;
  const confirmPassword = form.elements["repeat-password"].value;

  if (
    username.trim() === "" ||
    email.trim() === "" ||
    password.trim() === "" ||
    confirmPassword.trim() === ""
  ) {
    return;
  }

  errorMessage.style.display = "none";
  spinner.style.display = "inline-block";

  try {
    const response = await fetch("/users/register/details", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password,
        password_confirm: confirmPassword,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(`${data.detail}`);
    } else {
      const message = data.message;
      window.location.href = `/users/register/success?message=${encodeURIComponent(
        message
      )}`;
    }
  } catch (error) {
    errorMessage.textContent = error.message;
    errorMessage.style.display = "block";
  } finally {
    spinner.style.display = "none";
  }
});
