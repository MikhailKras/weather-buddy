import geonamescache
from fastapi import HTTPException, status
from pydantic import BaseModel, validator


class CityInput(BaseModel):
    city: str

    @validator('city')
    def valid_city(cls, city: str) -> list:
        gc = geonamescache.GeonamesCache()
        city_info = gc.search_cities(city.title())
        if not city_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
        return [city_info[x]['name'] for x in city_info]
