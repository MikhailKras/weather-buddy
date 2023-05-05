import aiohttp

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth.jwt import is_authenticated
from src.config import WEATHER_API_KEY

router = APIRouter(
    prefix='/weather',
    tags=['Weather-service']
)

templates = Jinja2Templates(directory='src/templates')


@router.get('/search', response_class=HTMLResponse)
async def get_page_weather_search(request: Request, is_auth: bool = Depends(is_authenticated)):
    return templates.TemplateResponse('city_weather_search.html', context={"request": request, "is_auth": is_auth})


@router.get('/{city}', response_class=HTMLResponse)
async def get_city_weather(request: Request, city: str, is_auth: bool = Depends(is_authenticated)):
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': city,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            if data.get('error'):
                return templates.TemplateResponse(
                    'city_weather_error.html', status_code=404, context={
                        "request": request,
                        "message": data['error']['message'],
                        "status_code": 404
                    }
                )
            weather_data = {
                'location': data['location']['name'],
                'temperature': data['current']['temp_c'],
                'weather_condition': data['current']['condition']['text'],
            }
            return templates.TemplateResponse(
                'city_weather_present.html', context={"request": request, "weather_data": weather_data, "is_auth": is_auth}
            )


