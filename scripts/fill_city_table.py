import asyncio
from typing import Optional

import aiohttp
import geonamescache
from sqlalchemy import insert, select

from src.auth.models import city
from src.config import WEATHER_API_KEY
from src.database import get_async_session


def get_all_cities() -> dict:
    gc = geonamescache.GeonamesCache()
    all_cities = gc.get_cities()
    return all_cities


def get_all_countries() -> dict:
    gc = geonamescache.GeonamesCache()
    all_countries = gc.get_countries()
    return all_countries


def get_city_dict_with_country(city_dict: dict) -> dict:
    countries = get_all_countries()
    country_code = city_dict['countrycode']
    city_dict.update(country=countries.get(country_code)['name'], name=city_dict['name'].title())
    return city_dict


async def get_region(latitude: float, longitude: float, city_name: str, alternate_names: list) -> Optional[str]:
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': f"{latitude},{longitude}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            if 'error' in data:
                return None
        if data['location']['name'] not in alternate_names:
            params.update(q=city_name)
            async with session.get(url=url, params=params) as response:
                data = await response.json()
                if 'error' in data:
                    return None
    return data['location'].get('region')


async def insert_city(city_dict: dict, region: Optional[str]):
    async for session in get_async_session():
        insert_query = insert(city).values(
            name=city_dict['name'],
            region=region,
            country=city_dict['country'],
            latitude=city_dict['latitude'],
            longitude=city_dict['longitude'],
            population=city_dict['population'],
            timezone=city_dict['timezone'],
            alternatenames=city_dict['alternatenames']
        )

        await session.execute(insert_query)
        await session.commit()


async def get_missing_cities():
    async for session in get_async_session():
        select_query = select(city)
        result = await session.execute(select_query)
        cities_in_db = result.fetchall()

        all_cities = get_all_cities()
        missing_cities = {}
        lat_long_in_db = {(cities_in_db[x][4], cities_in_db[x][5]) for x in range(len(cities_in_db))}
        all_lat_long = {(list(all_cities.values())[y]['latitude'], list(all_cities.values())[y]['longitude']) for y in range(len(all_cities.values()))}
        missing_lat_long = all_lat_long.difference(lat_long_in_db)
        for key, city_dict in all_cities.items():
            latitude, longitude = city_dict['latitude'], city_dict['longitude']
            if (latitude, longitude) in missing_lat_long:
                missing_cities[key] = city_dict
        return missing_cities


async def main():
    cities_dicts = await get_missing_cities()
    cities = cities_dicts.values()
    for city_dict in cities:
        region = await get_region(
            float(city_dict['latitude']),
            float(city_dict['longitude']),
            city_dict['name'],
            city_dict['alternatenames']
        )
        city_dict_with_country = get_city_dict_with_country(city_dict)
        await insert_city(city_dict_with_country, region)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
