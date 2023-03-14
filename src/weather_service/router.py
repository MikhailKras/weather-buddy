import aiohttp

from fastapi import APIRouter

from src.config import WEATHER_API_KEY

router = APIRouter(
    prefix='/weather',
    tags=['Weather-service']
)


@router.get('/{city}')
async def get_city_weather(city: str) -> dict:
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': city,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            return data


