from typing import Callable, List

import aiohttp

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, Response
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import is_authenticated
from src.config import WEATHER_API_KEY
from src.database import get_async_session
from src.weather_service.schemas import CityInDB, PrecipitationType, PrecipitationClothing
from src.weather_service.utils import search_cities_db, get_city_data_by_id, process_data, \
    get_data_from_clothing_document_by_precipitation, get_clothing_document, get_temperature_range, get_precipitation_type


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
async def find_city_name_matches(
        request: Request,
        city_input: str,
        session: AsyncSession = Depends(get_async_session),
        is_auth: bool = Depends(is_authenticated)
):
    city_info: List[CityInDB] = await search_cities_db(city_input.title(), session=session)
    if not city_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
    data = {
        "cities": [
            {
                "name": city_info[x].name,
                "country": city_info[x].country,
                "region": city_info[x].region,
                "latitude": city_info[x].latitude,
                "longitude": city_info[x].longitude,
                "population": city_info[x].population,
                "id": city_info[x].id
            }
            for x in range(len(city_info))
        ]
    }

    return templates.TemplateResponse(
        'city_names.html', context={"request": request, "data": data, "is_auth": is_auth}
    )


@router.get('/info/by_coordinates', response_class=HTMLResponse)
async def get_city_id_by_coordinates(
        request: Request,
        latitude: float,
        longitude: float,
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
            if not(
                    latitude - 1 < float(data['location']['lat']) < latitude + 1 and
                    longitude - 1 < float(data['location']['lon']) < longitude + 1
            ):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No information found for given coordinates')

    temperature_range = get_temperature_range(int(data['current']['feelslike_c']))
    precipitation = await get_precipitation_type(data['current']['condition']['code'])
    document = await get_clothing_document(temperature_range)
    db_clothing_data = get_data_from_clothing_document_by_precipitation(document, precipitation)
    location_data, weather_data, clothing_data = await process_data(weatherapi_data=data, db_clothing_data=db_clothing_data)

    return templates.TemplateResponse(
        'city_weather_present.html', context={
            "request": request,
            "weather_data": weather_data,
            "location_data": location_data,
            "clothing_data": clothing_data,
            "is_auth": is_auth,
        }
    )


@router.get('/info', response_class=HTMLResponse)
async def get_city_weather(
        request: Request,
        city_id: int,
        session: AsyncSession = Depends(get_async_session),
        is_auth: bool = Depends(is_authenticated)
):
    city_data = await get_city_data_by_id(city_id, session=session)

    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': f"{city_data.latitude},{city_data.longitude}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            if 'error' in data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data['error']['message'])
        if data['location']['name'].title() not in (city_data.name, *map(lambda name: name.title(), city_data.alternatenames)):
            params.update(q=f"{city_data.name}, {city_data.region}")
            async with session.get(url=url, params=params) as response:
                data = await response.json()
                if 'error' in data:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data['error']['message'])

    temperature_range = get_temperature_range(int(data['current']['feelslike_c']))
    precipitation = await get_precipitation_type(data['current']['condition']['code'])
    document = await get_clothing_document(temperature_range)
    db_clothing_data = get_data_from_clothing_document_by_precipitation(document, precipitation)
    location_data, weather_data, clothing_data = await process_data(data, city_data, db_clothing_data)

    return templates.TemplateResponse(
        'city_weather_present.html', context={
            "request": request,
            "weather_data": weather_data,
            "location_data": location_data,
            "clothing_data": clothing_data,
            "is_auth": is_auth,
        }
    )


@router.get('/clothes_data', response_model=PrecipitationClothing)
async def get_clothes_data(temperature: int, precipitation: PrecipitationType):
    temperature_range = get_temperature_range(temperature)
    document = await get_clothing_document(temperature_range)
    return get_data_from_clothing_document_by_precipitation(document, precipitation)
