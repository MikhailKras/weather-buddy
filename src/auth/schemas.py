import datetime
import re

from fastapi import HTTPException, status

from pydantic import BaseModel, validator, EmailStr

import geonamescache

PASSWORD_PATTERN = re.compile(r'(?=.*\d+.*)(?=.*[a-zA-Z]+.*)')


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    city: str

    @validator('password')
    def valid_password(cls, password: str) -> str:
        if not re.match(PASSWORD_PATTERN, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must contain at least'
                       'one digit, at least one letter'
            )
        if len(password) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Length of password must be more than 6 characters'
            )
        return password

    @validator('city')
    def valid_city(cls, city: str) -> str:
        gc = geonamescache.GeonamesCache()
        city_info = gc.get_cities_by_name(city.title())
        if not city_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
        return city.title()


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    city: str


class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    city: str
    registered_at: datetime.datetime
    disabled: bool


class Token(BaseModel):
    access_token: str
    token_type: str
