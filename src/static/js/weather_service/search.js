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

  fetch(`/weather/city_names?city_input=${cityInput}`)
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.detail);
        });
      }
      window.location.href = `/weather/city_names?city_input=${encodeURIComponent(
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

function searchByCoords(event) {
  event.preventDefault();
  const latitudeInput = document.getElementById("latitude").value;
  const longitudeInput = document.getElementById("longitude").value;
  const errorMessage = document.getElementById("error-message-coords");
  const spinner = document.querySelector(
    "#submit-button-coords .spinner-border"
  );

  if (latitudeInput.trim() === "" || longitudeInput.trim() === "") {
    return;
  }

  errorMessage.style.display = "none";
  spinner.style.display = "inline-block";

  redirect_url =
    "/weather/info/by_coordinates?latitude=" +
    encodeURIComponent(latitudeInput) +
    "&longitude=" +
    encodeURIComponent(longitudeInput);
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
    })
    .finally(() => {
      spinner.style.display = "none";
    });
}
