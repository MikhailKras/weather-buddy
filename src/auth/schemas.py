import re

from fastapi import HTTPException

from pydantic import BaseModel, validator, EmailStr, Field

import geonamescache

PASSWORD_PATTERN = re.compile(r'(?=.*\d+.*)(?=.*[a-zA-Z]+.*)')


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=7, max_length=128)
    city: str

    @validator('password')
    def valid_password(cls, password: str) -> str:
        if not re.match(PASSWORD_PATTERN, password):
            raise HTTPException(
                status_code=400,
                detail='Password must contain at least'
                       'one digit, at least one letter'
                       'and it is length must be more'
                       'than 6 characters')
        return password

    @validator('city')
    def valid_city(cls, city: str) -> str:
        gc = geonamescache.GeonamesCache()
        city_info = gc.get_cities_by_name(city.title())
        if not city_info:
            raise HTTPException(status_code=400, detail='Invalid city!')
        return city.title()


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    city: str
