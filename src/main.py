import requests

from fastapi import FastAPI

from src.config import WEATHER_API_KEY

app = FastAPI()


@app.get('/weather/{city}')
def get_city_weather(city: str):
    payload = {
        'key': WEATHER_API_KEY,
        'q': city,
    }
    url = 'http://api.weatherapi.com/v1/current.json'
    response_json = requests.get(url, params=payload).json()
    return response_json
