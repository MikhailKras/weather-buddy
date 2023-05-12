function searchByCity(event) {
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

function searchByCoords(event) {
  event.preventDefault();
  const latitudeInput = document.getElementById("latitude").value;
  const longitudeInput = document.getElementById("longitude").value;
  const errorMessage = document.getElementById("error-message-coords");

  errorMessage.style.display = "none";

  redirect_url = "/weather/info?latitude=" + encodeURIComponent(latitudeInput) + "&longitude=" + encodeURIComponent(longitudeInput) + "&city=" + encodeURIComponent('search_by_coordinates');
  fetch(redirect_url)
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      window.location.href = redirect_url;
    })
    .catch((error) => {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    });
}
