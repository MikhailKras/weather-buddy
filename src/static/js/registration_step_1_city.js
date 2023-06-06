function searchByCity(event) {
  event.preventDefault();
  const cityInput = document.getElementById("city").value;
  const errorMessage = document.getElementById("error-message");

  errorMessage.style.display = "none";

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
    });
}
