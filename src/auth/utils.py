from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user
from src.database import get_async_session


async def get_user_by_username(
        username: str,
        session: AsyncSession = Depends(get_async_session)
):
    select_query = select(user).where(user.c.username == username)
    result = await session.execute(select_query)
    return result.all()


async def get_user_by_email(
        email: str,
        session: AsyncSession = Depends(get_async_session)
):
    select_query = select(user).where(user.c.email == email)
    result = await session.execute(select_query)
    return result.all()
