from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.security import get_password_hash
from src.database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)


@router.post('/register')
async def register_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        city=user.city,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
