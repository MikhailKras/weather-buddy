from typing import Optional, Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user
from src.auth.schemas import UserInDB
from src.auth.security import verify_password
from src.database import get_async_session


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
