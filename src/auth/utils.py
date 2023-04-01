from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user
from src.auth.schemas import UserInDB, AuthUser
from src.auth.security import verify_password
from src.database import get_async_session


async def get_user_by_username(
        username: str,
        session: AsyncSession = Depends(get_async_session)
):
    select_query = select(user).where(user.c.username == username)
    result = await session.execute(select_query)
    test = []
    for row in result:
        test.append(row.items())
    print(test)


async def get_user_by_email(
        email: str,
        session: AsyncSession = Depends(get_async_session)
):
    select_query = select(user).where(user.c.email == email)
    result = await session.execute(select_query)
    return result.all()


def authenticate_user(
        auth_data: AuthUser,
        session: AsyncSession = Depends(get_async_session)
):
    user_data = await get_user_by_username(auth_data.username, session=session)
    if not user:
        return False
    if not verify_password(auth_data.password, user_data.hashed_password):
        return False
    return user
