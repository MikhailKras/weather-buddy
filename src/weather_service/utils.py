from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import city
from src.database import get_async_session
from src.weather_service.schemas import CityInDB


async def search_cities_db(
        city_name: str,
        session: AsyncSession = Depends(get_async_session)
) -> List[CityInDB]:
    column_names = [column.name for column in city.columns]
    select_query = select(city)
    result = await session.execute(select_query)
    cities_in_db = result.fetchall()
    cities_in_db_with_column_names = [{column_name: value for column_name, value in zip(column_names, row)} for row in cities_in_db]

    result = []
    for city_dict in cities_in_db_with_column_names:
        if city_name in (city_dict['name'].title(), *map(lambda name: name.title(), city_dict['alternatenames'])):
            result.append(CityInDB(**city_dict))
    return result


async def get_city_data_by_id(
        city_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> CityInDB:
    column_names = [column.name for column in city.columns]
    select_query = select(city).where(city.c.id == city_id)
    result = await session.execute(select_query)
    row = result.fetchone()
    city_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return CityInDB(**city_dict)


async def process_weather_data(data):
    location_data = {
        'location': data['location']['name'],
        'region': data['location']['region'],
        'country': data['location']['country'],
        'latitude': data['location']['lat'],
        'longitude': data['location']['lon'],
        'timezone': data['location']['tz_id'],
        'local time': data['location']['localtime'],
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
    return location_data, weather_data
