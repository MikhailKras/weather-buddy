from typing import Callable

import aiohttp
import geonamescache

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, Response
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from src.auth.jwt import is_authenticated
from src.config import WEATHER_API_KEY


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                errors = exc.errors()
                error_messages = []
                for error in errors:
                    error_messages.append(error['msg'].replace('value', error['loc'][1]).capitalize())
                detail = '. '.join(error_messages)
                raise HTTPException(status_code=400, detail=detail)

        return custom_route_handler


router = APIRouter(
    prefix='/weather',
    tags=['Weather-service'],
    route_class=ValidationErrorLoggingRoute
)

templates = Jinja2Templates(directory='src/templates')


@router.get('/search', response_class=HTMLResponse)
async def get_page_weather_search(request: Request, is_auth: bool = Depends(is_authenticated)):
    return templates.TemplateResponse('city_weather_search.html', context={"request": request, "is_auth": is_auth})


@router.get('/city_names', response_class=HTMLResponse)
async def find_city_name_matches(request: Request, city_input: str, is_auth: bool = Depends(is_authenticated)):
    gc = geonamescache.GeonamesCache()
    city_info = gc.search_cities(city_input.title())
    if not city_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
    city_names = [city_info[x]['name'] for x in range(len(city_info))]
    country_codes = [city_info[x]['countrycode'] for x in range(len(city_info))]
    countries_info: dict = gc.get_countries()
    country_names = [countries_info.get(country_code)['name'] for country_code in country_codes]
    coordinates = [{'latitude': city_info[x]['latitude'], 'longitude': city_info[x]['longitude']} for x in range(len(city_info))]
    data = {'cities': [{'name': name, 'country': country, 'coordinates': coords} for name, country, coords in zip(city_names, country_names, coordinates)]}
    return templates.TemplateResponse(
        'city_names.html', context={"request": request, "data": data, "is_auth": is_auth}
    )


@router.get('/info', response_class=HTMLResponse)
async def get_city_weather(
        request: Request,
        latitude: float,
        longitude: float,
        city: str,
        is_auth: bool = Depends(is_authenticated)
):
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid coordinates!')
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': f"{latitude},{longitude}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            if 'error' in data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data['error']['message'])
            if city == 'search_by_coordinates':
                if not(
                        latitude - 1 < float(data['location']['lat']) < latitude + 1 and
                        longitude - 1 < float(data['location']['lon']) < longitude + 1
                ):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No information found for given coordinates')
        if city != 'search_by_coordinates' and data['location']['name'] != city:
            params.update(q=city)
            async with session.get(url=url, params=params) as response:
                data = await response.json()

    location_data = {
        'location': data['location']['name'],
        'region': data['location']['region'],
        'country': data['location']['country'],
        'latitude': data['location']['lat'],
        'longitude': data['location']['lon'],
        'timezone': data['location']['tz_id'],
        'local time': data['location']['localtime']
    }
    weather_data = {
        'temperature, °C': data['current']['temp_c'],
        'feels like, °C': data['current']['feelslike_c'],
        'weather condition': data['current']['condition']['text'],
        'last updated': data['current']['last_updated'],
        'wind, kph': data['current']['wind_kph'],
        'humidity, %': data['current']['humidity'],
        'cloudiness, %': data['current']['cloud'],

    }

    return templates.TemplateResponse(
        'city_weather_present.html', context={
            "request": request,
            "weather_data": weather_data,
            "location_data": location_data,
            "is_auth": is_auth,
        }
    )

