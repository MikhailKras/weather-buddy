import json
from typing import Callable, List, Optional

import aiohttp

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import is_authenticated
from src.auth.schemas import UserInDB
from src.config import WEATHER_API_KEY
from src.database import get_async_session, redis_db
from src.utils import get_jinja_templates
from src.weather_service.schemas import CityInDB, SearchHistoryCityName, SearchHistoryCoordinates
from src.weather_service.utils import search_cities_db, get_city_data_by_id, process_data, \
    get_data_from_clothing_document_by_precipitation, get_clothing_document, get_temperature_range, get_precipitation_type, \
    insert_search_history_city_name, insert_search_history_coordinates


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

templates = get_jinja_templates()


@router.get('/search', response_class=HTMLResponse)
async def get_page_weather_search(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    return templates.TemplateResponse('city_weather_search.html', context={"request": request, "is_auth": user_data})


@router.get('/validate', response_class=JSONResponse)
async def validate_city_input(
        city_input: str,
        session: AsyncSession = Depends(get_async_session)
):
    formatted_city_input = city_input.title().strip()

    cached_data_json = await redis_db.redis.get(formatted_city_input)

    if cached_data_json:
        cached_data = json.loads(cached_data_json)
        return JSONResponse(content=cached_data)

    city_info: List[CityInDB] = await search_cities_db(formatted_city_input, session=session)
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
    await redis_db.redis.set(formatted_city_input, json.dumps(data))
    await redis_db.redis.expire(formatted_city_input, 3600)

    return JSONResponse(content=data)


@router.get('/cities', response_class=HTMLResponse)
async def get_city_name_matches(
        request: Request,
        city_input: str,
        session: AsyncSession = Depends(get_async_session),
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    formatted_city_input = city_input.title().strip()
    data_json = await redis_db.redis.get(formatted_city_input)

    if data_json is None:
        data_json_response = await validate_city_input(formatted_city_input, session=session)
        data_json = data_json_response.body.decode()

    data = json.loads(data_json)

    return templates.TemplateResponse(
        'city_names.html', context={"request": request, "data": data, "is_auth": user_data}
    )


@router.get('/info/by_coordinates', response_class=JSONResponse)
async def get_weather_data_by_coordinates(
        latitude: float,
        longitude: float,
        session: AsyncSession = Depends(get_async_session),
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    key_name = f"{latitude}:{longitude}"
    cached_data_json = await redis_db.redis.get(key_name)

    if cached_data_json:
        cached_data = json.loads(cached_data_json)
        return JSONResponse(content=cached_data)

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid coordinates!')
    url = 'http://api.weatherapi.com/v1/forecast.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': f"{latitude},{longitude}",
    }
    async with aiohttp.ClientSession() as weatherapi_session:
        async with weatherapi_session.get(url=url, params=params) as response:
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
    location_data, weather_data, clothing_data, forecast_data = await process_data(weatherapi_data=data, db_clothing_data=db_clothing_data)

    if user_data is not None:
        search_history_coordinates = SearchHistoryCoordinates(
            user_id=user_data.id,
            latitude=latitude,
            longitude=longitude,
            place_name=location_data['location'],
            region=location_data['region'],
            country=location_data['country']
        )
        await insert_search_history_coordinates(search_history_coordinates=search_history_coordinates, session=session)

    result_data = {
        "weather_data": weather_data,
        "forecast_data": forecast_data,
        "location_data": location_data,
        "clothing_data": clothing_data,
    }

    await redis_db.redis.set(key_name, json.dumps(result_data))
    await redis_db.redis.expire(key_name, 60)

    return JSONResponse(content=result_data)


@router.get('/info/by_coordinates/html', response_class=HTMLResponse)
async def get_weather_data_by_coordinates_html(
        request: Request,
        latitude: float,
        longitude: float,
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    result_data_json = await redis_db.redis.get(f"{latitude}:{longitude}")

    if result_data_json is None:
        result_data_json_response = await get_weather_data_by_coordinates(latitude, longitude, user_data=user_data)
        result_data_json = result_data_json_response.body.decode()

    result_data = json.loads(result_data_json)

    result_data.update({"request": request, "is_auth": user_data})

    return templates.TemplateResponse(
        'city_weather_present.html', context=result_data)


@router.get('/info', response_class=HTMLResponse)
async def get_city_weather(
        request: Request,
        city_id: int,
        session: AsyncSession = Depends(get_async_session),
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    city_data = await get_city_data_by_id(city_id, session=session)

    url = 'http://api.weatherapi.com/v1/forecast.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': f"{city_data.latitude},{city_data.longitude}",
        'days': 3,
    }
    async with aiohttp.ClientSession() as weatherapi_session:
        async with weatherapi_session.get(url=url, params=params) as response:
            data = await response.json()
            if 'error' in data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data['error']['message'])
        if data['location']['name'].title() not in (city_data.name, *map(lambda name: name.title(), city_data.alternatenames)):
            params.update(q=f"{city_data.name}, {city_data.region}, {city_data.country}")
            async with weatherapi_session.get(url=url, params=params) as response:
                data = await response.json()
                if 'error' in data:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data['error']['message'])

    temperature_range = get_temperature_range(int(data['current']['feelslike_c']))
    precipitation = await get_precipitation_type(data['current']['condition']['code'])
    document = await get_clothing_document(temperature_range)
    db_clothing_data = get_data_from_clothing_document_by_precipitation(document, precipitation)
    location_data, weather_data, clothing_data, forecast_data = await process_data(data, city_data, db_clothing_data)

    if user_data is not None:
        search_history_city_name = SearchHistoryCityName(user_id=user_data.id, city_id=city_id)
        await insert_search_history_city_name(search_history_city_name=search_history_city_name, session=session)

    return templates.TemplateResponse(
        'city_weather_present.html', context={
            "request": request,
            "weather_data": weather_data,
            "forecast_data": forecast_data,
            "location_data": location_data,
            "clothing_data": clothing_data,
            "is_auth": user_data,
        }
    )
