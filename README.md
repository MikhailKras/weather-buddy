<img src="src/static/images/logo_weather_buddy_rounded.png" alt="WeatherBuddy Logo" width="200" height="200">

# WeatherBuddy

### Backend Technologies

[![Python](https://img.shields.io/badge/Python-3.11-416b9a.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.96-409484.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.8-336791.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0.6-419053.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0.11-c84126.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.3.1-b0ca60.svg)](https://docs.celeryproject.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.3.1-0E7FBF.svg)](https://docs.pytest.org/en/stable/)


### Frontend Technologies

[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-7811f7.svg)](https://getbootstrap.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-eee06a.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS](https://img.shields.io/badge/CSS-3-523f79.svg)](https://developer.mozilla.org/en-US/docs/Web/CSS)

### Live Demo: [https://weather-buddy.net](https://weather-buddy.net)

### Example of search process

![Website Demo](src/static/images/home/search_city_process.webp)

This is a Python web application built with FastAPI that provides current weather information. The application utilizes a PostgreSQL database that contains a table with 25,000+ cities. Users can retrieve the following information for each city:

- Current clothing recommendations based on weather conditions (clothing information stored in MongoDB)
- Current weather and location information (from the PostgreSQL database, including population, timezone, region, country, etc.)

### Prerequisites

Before you proceed, please make sure you have the following installed on your machine:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Getting Started

- Clone this git repo

```batch
git clone https://github.com/MikhailKras/weather-buddy.git
```

- Change your working directory to the `weather-buddy` directory:

```batch
cd weather-buddy
```

- Set enviroment variables in [.env.prod](https://github.com/MikhailKras/weather-buddy/blob/master/.env.prod)

- Build docker image:

```batch
docker compose --env-file .env.prod build app
```

- Up docker compose:

```batch
docker compose --env-file .env.prod up -d
```
After the successful process, you can access the Weather Buddy app by going to http://localhost:9999 in your web browser.

### Features

- User authentication with OAuth 2.0 and bearer JWT token
- Two-step registration process:
  - Step 1: Choose city name
  - Step 2: Input additional information (username, email, password)
- Email verification with synchronous SMTP using `smtplib` and Celery for asynchronous email tasks
- Rate limiter for several endpoints with FastAPI-Limiter (using Redis)
- CSS styles and Bootstrap 5 framework for frontend
- JavaScript scripts for sending requests to the API
- Search history: Track and display user's search history for cities and coordinates

## Clothing Document Example (MongoDB)

```json
{
  "_id": "64834ea1fda0d16eceebf0ca",
  "temperatureRange": { "min": 10, "max": 15 },
  "precipitation": {
    "None": {
      "UpperBody": {
        "BaseLayer": { "clothingItems": ["Light long-sleeve shirt"] },
        "MidLayer": { "clothingItems": ["Light jacket"] },
        "OuterLayerShell": { "clothingItems": [] },
        "Accessories": { "clothingItems": ["Hat"] }
      },
      "LowerBody": {
        "BaseLayer": { "clothingItems": ["Light pants"] },
        "MidLayer": { "clothingItems": [] },
        "OuterLayerShell": { "clothingItems": [] },
        "Accessories": { "clothingItems": [] }
      },
      "Footwear": { "clothingItems": ["Sneakers"] }
    },
    "Rain": {
      "UpperBody": {
        "BaseLayer": { "clothingItems": ["Light long-sleeve shirt"] },
        "MidLayer": { "clothingItems": ["Raincoat"] },
        "OuterLayerShell": { "clothingItems": [] },
        "Accessories": { "clothingItems": ["Umbrella"] }
      },
      "LowerBody": {
        "BaseLayer": { "clothingItems": ["Light pants"] },
        "MidLayer": { "clothingItems": [] },
        "OuterLayerShell": { "clothingItems": [] },
        "Accessories": { "clothingItems": [] }
      },
      "Footwear": { "clothingItems": ["Waterproof sneakers"] }
    }
  }
}
```
## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/MikhailKras/weather-buddy/blob/master/LICENSE.md) file for details.
