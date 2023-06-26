import datetime
from typing import Optional, Union, Dict, List, Tuple

from fastapi import Depends, Request, HTTPException, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from pytz import timezone, utc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user, email_verification
from src.auth.schemas import UserInDB, UserEmailVerificationInfo, CityInDB
from src.auth.security import verify_password
from src.database import get_async_session
from src.models import city, search_history_city_name_db, search_history_coordinates_db
from src.weather_service.schemas import SearchHistoryCityName, SearchHistoryCoordinates


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


async def get_user_by_username(
        username: str,
        session: AsyncSession = Depends(get_async_session)
) -> Optional[UserInDB]:
    column_names = [column.name for column in user.columns]
    select_query = select(user).where(user.c.username == username)
    result = await session.execute(select_query)
    row = result.fetchone()
    if not row:
        return
    user_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return UserInDB(**user_dict)


async def get_user_by_email(
        email: str,
        session: AsyncSession = Depends(get_async_session)
) -> Optional[UserInDB]:
    column_names = [column.name for column in user.columns]
    select_query = select(user).where(user.c.email == email)
    result = await session.execute(select_query)
    row = result.fetchone()
    if not row:
        return
    user_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return UserInDB(**user_dict)


async def get_user_by_user_id(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> Optional[UserInDB]:
    column_names = [column.name for column in user.columns]
    select_query = select(user).where(user.c.id == user_id)
    result = await session.execute(select_query)
    row = result.fetchone()
    if not row:
        return
    user_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return UserInDB(**user_dict)


async def authenticate_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
) -> Union[UserInDB, bool]:
    user_data = await get_user_by_username(form_data.username, session=session)
    if not user_data:
        return False
    if not verify_password(form_data.password, user_data.hashed_password):
        return False
    return user_data


async def get_user_email_verification_info(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> Optional[UserEmailVerificationInfo]:
    column_names = [column.name for column in email_verification.columns]
    select_query = select(email_verification).where(email_verification.c.user_id == user_id)
    result = await session.execute(select_query)
    row = result.fetchone()
    if not row:
        return
    user_email_verification_info_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return UserEmailVerificationInfo(**user_email_verification_info_dict)


async def get_user_city_data(
        city_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> Optional[CityInDB]:
    column_names = [column.name for column in city.columns]
    select_query = select(city).where(city.c.id == city_id)
    result = await session.execute(select_query)
    row = result.fetchone()
    if not row:
        return
    user_city_data_dict = {column_name: value for column_name, value in zip(column_names, row.tuple())}
    return CityInDB(**user_city_data_dict)


async def get_search_history_data(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> Tuple[Optional[List[SearchHistoryCityName]], Optional[List[SearchHistoryCoordinates]]]:
    city_name_select_query = select(search_history_city_name_db).where(search_history_city_name_db.c.user_id == user_id)
    coordinates_select_query = select(search_history_coordinates_db).where(search_history_coordinates_db.c.user_id == user_id)

    city_name_result = await session.execute(city_name_select_query)
    city_name_rows = city_name_result.fetchall()
    coordinates_result = await session.execute(coordinates_select_query)
    coordinates_rows = coordinates_result.fetchall()

    city_name_search_history_data = None
    coordinates_search_history_data = None

    if city_name_rows:
        column_names_city_name = [column.name for column in search_history_city_name_db.columns]
        city_name_search_history_data = [
            SearchHistoryCityName(**{column_name: value for column_name, value in zip(column_names_city_name, row)})
            for row in city_name_rows
        ]

    if coordinates_rows:
        column_names_coordinates = [column.name for column in search_history_coordinates_db.columns]
        coordinates_search_history_data = [
            SearchHistoryCoordinates(**{column_name: value for column_name, value in zip(column_names_coordinates, row)})
            for row in coordinates_rows
        ]

    return city_name_search_history_data, coordinates_search_history_data
