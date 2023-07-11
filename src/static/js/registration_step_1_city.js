function searchByCity(event) {
  event.preventDefault();
  const cityInput = document.getElementById("city").value;
  const errorMessage = document.getElementById("error-message");
  const spinner = document.querySelector("#submit-button .spinner-border");

  if (cityInput.trim() === "") {
    return;
  }

  errorMessage.style.display = "none";
  spinner.style.display = "inline-block";

  fetch(
    `/users/register/city/choose_city_name?city_input=${encodeURIComponent(
      cityInput
    )}`
  )
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      window.location.href = `/users/register/city/choose_city_name?city_input=${encodeURIComponent(
        cityInput
      )}`;
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    })
    .finally(() => {
      spinner.style.display = "none";
    });
}
