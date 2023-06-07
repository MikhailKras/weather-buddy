import datetime
import re
from typing import List

from fastapi import HTTPException, status

from pydantic import BaseModel, validator, EmailStr, root_validator

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
PASSWORD_PATTERN = re.compile(r'(?=.*\d+.*)(?=.*[a-zA-Z]+.*)')


class UserCreateStep1(BaseModel):
    city_id: int


class UserCreateStep2(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('username')
    def valid_username(cls, username: str):
        if not re.match(USERNAME_PATTERN, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username must be between 3 and 20 characters long and '
                       'can only contain alphanumeric characters, underscores, and hyphens'
            )
        return username

    @validator('password')
    def valid_password(cls, password: str) -> str:
        if not re.match(PASSWORD_PATTERN, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must contain at least '
                       'one digit, at least one letter'
            )
        if len(password) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must contain at least 7 characters'
            )
        return password


class UserUpdateData(BaseModel):
    username: str
    email: EmailStr


class UserUpdateCity(BaseModel):
    city_id: int


class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    city_id: int
    registered_at: datetime.datetime
    disabled: bool


class UserEmailVerificationInfo(BaseModel):
    id: int
    user_id: int
    token: str
    verified: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    repeat_password: str

    @root_validator
    def check_passwords_match(cls, values):
        current_password = values.get('current_password')
        new_password = values.get('new_password')
        repeat_password = values.get('repeat_password')
        if new_password != repeat_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The provided passwords do not match'
            )
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='New password must be different from current password'
            )
        if not re.match(PASSWORD_PATTERN, new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='New password must contain at least '
                       'one digit, at least one letter'
            )
        if len(new_password) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must contain at least 7 characters'
            )
        return values


class CityInDB(BaseModel):
    id: int
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    population: int
    timezone: str
    alternatenames: List[str]


class EmailPasswordReset(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    password: str
    password_confirm: str

    @root_validator
    def check_passwords_match(cls, values):
        password = values.get('password')
        password_confirm = values.get('password_confirm')
        if password != password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The provided passwords do not match'
            )
        if not re.match(PASSWORD_PATTERN, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='New password must contain at least '
                       'one digit, at least one letter'
            )
        if len(password) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must contain at least 7 characters'
            )
        return values
