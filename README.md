# WeatherBuddy

### Backend Technologies

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.96-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.8-blue.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0.6-green.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0.11-red.svg)](https://redis.io/)

### Frontend Technologies

[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)](https://getbootstrap.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS](https://img.shields.io/badge/CSS-3-blueviolet.svg)](https://developer.mozilla.org/en-US/docs/Web/CSS)


This is a Python web application built with FastAPI that provides current weather information. The application utilizes a PostgreSQL database that contains a table with 25,000+ cities. Users can retrieve the following information for each city:

- Current clothing recommendations based on weather conditions (clothing information stored in MongoDB)
- Current weather and location information (from the PostgreSQL database, including population, timezone, region, country, etc.)

### Features

- User authentication with OAuth 2.0 and bearer JWT token
- Two-step registration process:
  - Step 1: Choose city name
  - Step 2: Input additional information (username, email, password)
- Email verification with FastAPI-Email and sending emails using Google SMTP
- Rate limiter for several endpoints with FastAPI-Limiter (using Redis)
- CSS styles and Bootstrap 5 framework for frontend
- JavaScript scripts for sending requests to the API

### Planned Features

- Docker Compose integration
- Deployment of the application with Nginx


## Clothing Document Example (MongoDB)

```json
{ 
    "_id": "64834ea1fda0d16eceebf0ca",
    "temperatureRange": { "min": 10, "max": 15 },
    "precipitation": {
        "None": {
            "UpperBody": {
                "BaseLayer": { "clothingItems": [ "Light long-sleeve shirt" ] },
                "MidLayer": { "clothingItems": [ "Light sweater" ] },
                "OuterLayerShell": { "clothingItems": [] },
                "Accessories": { "clothingItems": [ "Scarf" ] }
            },
            "LowerBody": {
                "BaseLayer": { "clothingItems": [ "Light pants" ] },
                "MidLayer": { "clothingItems": [] },
                "OuterLayerShell": { "clothingItems": [] },
                "Accessories": { "clothingItems": [] }
            },
            "Footwear": { "clothingItems": [ "Sneakers" ] }
        },
        "Rain": {
            "UpperBody": {
                "BaseLayer": { "clothingItems": [ "Light long-sleeve shirt" ] },
                "MidLayer": { "clothingItems": [ "Light sweater", "Raincoat" ] },
                "OuterLayerShell": { "clothingItems": [] },
                "Accessories": { "clothingItems": [ "Scarf" ] }
            },
            "LowerBody": {
                "BaseLayer": { "clothingItems": [ "Light pants" ] },
                "MidLayer": { "clothingItems": [] },
                "OuterLayerShell": { "clothingItems": [] },
                "Accessories": { "clothingItems": [] }
            },
            "Footwear": { "clothingItems": [ "Sneakers", "Rain boots" ] }
        }
    }
}
