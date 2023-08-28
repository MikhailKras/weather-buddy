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

  const redirect_url =
    "/weather/info/by_coordinates?latitude=" +
    encodeURIComponent(latitudeInput) +
    "&longitude=" +
    encodeURIComponent(longitudeInput);

  // Use the History API to update the browser's URL
  history.pushState(null, null, redirect_url);

  // Check if there's an ongoing request
  if (!searchByCoords.pendingRequest) {
    searchByCoords.pendingRequest = true;

    fetch(redirect_url)
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.detail);
          });
        }
        // Handle the redirection after the request is successful
        return response.text();
      })
      .then((html) => {
        // Render the HTML page from the response
        document.body.innerHTML = html;
      })
      .catch((error) => {
        errorMessage.textContent = error.message;
        errorMessage.style.display = "block";
      })
      .finally(() => {
        searchByCoords.pendingRequest = false;
        spinner.style.display = "none";
      });
  }
}
