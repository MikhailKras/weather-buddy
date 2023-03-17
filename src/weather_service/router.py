import aiohttp

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.config import WEATHER_API_KEY

router = APIRouter(
    prefix='/weather',
    tags=['Weather-service']
)

templates = Jinja2Templates(directory='templates')


@router.get('/search', response_class=HTMLResponse)
async def get_page_weather_search(request: Request):
    return templates.TemplateResponse('city_weather_search.html', context={"request": request})


@router.get('/{city}', response_class=HTMLResponse)
async def get_city_weather(request: Request, city: str):
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': city,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            weather_data = {
                'location': data['location']['name'],
                'temperature': data['current']['temp_c'],
                'weather_condition': data['current']['condition']['text']
            }
            return templates.TemplateResponse('city_weather_present.html', context={"request": request, "weather_data": weather_data})


