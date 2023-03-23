from fastapi import APIRouter, Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user
from src.auth.schemas import UserCreate, UserResponse
from src.auth.security import get_password_hash
from src.database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)


@router.post('/register', response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    insert_query = insert(user).values(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        city=user_data.city,
    )
    await session.execute(insert_query)
    await session.commit()

    response = {
        'username': user_data.username,
        'email': user_data.email,
        'city': user_data.city,
    }
    return response
