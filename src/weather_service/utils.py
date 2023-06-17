from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import MONGODB_COLLECTION_NAME
from src.models import city
from src.database import get_async_session, mongo_db
from src.weather_service.schemas import CityInDB, TemperatureRange, ClothesDataDocument, PrecipitationClothing, PrecipitationType


async def search_cities_db(
        city_name: str,
        session: AsyncSession = Depends(get_async_session)
) -> List[CityInDB]:
    column_names = [column.name for column in city.columns]
    select_query = select(city).order_by(city.c.population.desc())
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


async def process_data(
        weatherapi_data: dict,
        db_city_data: CityInDB = None,
        db_clothing_data: PrecipitationClothing = None
):
    if db_clothing_data:
        clothing_data = {
            'upper body': {
                'Base Layer': db_clothing_data.UpperBody.BaseLayer.clothingItems,
                'Mid Layer': db_clothing_data.UpperBody.MidLayer.clothingItems,
                'Outer Layer': db_clothing_data.UpperBody.OuterLayerShell.clothingItems,
                'Accessories': db_clothing_data.UpperBody.Accessories.clothingItems,
            },
            'lower body': {
                'Base Layer': db_clothing_data.LowerBody.BaseLayer.clothingItems,
                'Mid Layer': db_clothing_data.LowerBody.MidLayer.clothingItems,
                'Outer Layer': db_clothing_data.LowerBody.OuterLayerShell.clothingItems,
                'Accessories': db_clothing_data.LowerBody.Accessories.clothingItems,
            },
            'footwear': db_clothing_data.Footwear.clothingItems,
        }
    else:
        clothing_data = None

    location_data = {
        'location': weatherapi_data['location']['name'],
        'region': weatherapi_data['location']['region'],
        'country': weatherapi_data['location']['country'],
        'latitude': weatherapi_data['location']['lat'],
        'longitude': weatherapi_data['location']['lon'],
        'timezone': weatherapi_data['location']['tz_id'],
        'local time': weatherapi_data['location']['localtime'],
    }
    weather_data = {
        'temperature, °C': weatherapi_data['current']['temp_c'],
        'feels like, °C': weatherapi_data['current']['feelslike_c'],
        'weather condition': weatherapi_data['current']['condition']['text'],
        'last updated': weatherapi_data['current']['last_updated'],
        'wind, kph': weatherapi_data['current']['wind_kph'],
        'humidity, %': weatherapi_data['current']['humidity'],
        'cloudiness, %': weatherapi_data['current']['cloud'],
        'img url': weatherapi_data['current']['condition']['icon']
    }

    forecast_info = weatherapi_data['forecast']['forecastday']
    formatted_forecast = []

    for day in forecast_info:
        date = day['date']
        max_temp = day['day']['maxtemp_c']
        min_temp = day['day']['mintemp_c']
        condition = day['day']['condition']['text']

        hourly_forecast = day['hour']
        formatted_hourly_forecast = []

        for hour in hourly_forecast:
            time = hour['time']
            temp = hour['temp_c']
            condition = hour['condition']['text']
            img_url = hour['condition']['icon']

            formatted_hourly_forecast.append({
                'time': time,
                'temp': temp,
                'condition': condition,
                'img_url': img_url
            })

        formatted_forecast.append({
            'date': date,
            'max_temp': max_temp,
            'min_temp': min_temp,
            'condition': condition,
            'hourly_forecast': formatted_hourly_forecast
        })

    if db_city_data:
        location_data.update(population=db_city_data.population)
    return location_data, weather_data, clothing_data, formatted_forecast


def get_temperature_range(temperature: int) -> TemperatureRange:
    if temperature >= 30:
        temperature_min = 25
        temperature_max = 30
    elif temperature <= -25:
        temperature_min = -20
        temperature_max = -25
    else:
        temperature_min = (temperature // 5) * 5
        temperature_max = temperature_min + 5
    return TemperatureRange(min=temperature_min, max=temperature_max)


async def get_clothing_document(temperature_range: TemperatureRange) -> ClothesDataDocument:
    collection = mongo_db.db[MONGODB_COLLECTION_NAME]

    filter_collection = {
        "temperatureRange.min": temperature_range.min,
        "temperatureRange.max": temperature_range.max
    }
    document = await collection.find_one(filter_collection)

    if not document:
        temperature_range_str = f"{temperature_range.min}-{temperature_range.max} degrees"
        detail_message = f"Clothing document for temperature range {temperature_range_str} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message)

    return ClothesDataDocument(**document)


async def get_precipitation_type(code_condition: int) -> Optional[PrecipitationType]:
    collection = mongo_db.db["weatherapi_codes"]
    filter_collection = {
        "code": code_condition
    }
    document = await collection.find_one(filter_collection)

    if not document:
        detail_message = f"Precipitation type for code {code_condition} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message)

    return PrecipitationType(value=document['precipitation'])


def get_data_from_clothing_document_by_precipitation(
        document: ClothesDataDocument,
        precipitation: Optional[PrecipitationType],
) -> Optional[PrecipitationClothing]:
    if precipitation is None:
        return None
    try:
        match precipitation.value:
            case "None":
                data_for_current_precipitation = document.precipitation.none
            case "Rain":
                data_for_current_precipitation = document.precipitation.Rain
            case "Snow":
                data_for_current_precipitation = document.precipitation.Snow
            case other:
                return None
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clothing data found for current precipitation"
        )

    return data_for_current_precipitation
