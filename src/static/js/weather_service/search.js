function searchForOperation(event) {
  event.preventDefault();
  const cityInput = document.getElementById("city").value;
  const errorMessage = document.getElementById("error-message");
  
  errorMessage.style.display = "none";

  fetch(`/weather/city_names?city_input=${cityInput}`)
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      window.location.href = `/weather/city_names?city_input=${encodeURIComponent(cityInput)}`;
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    });
}
