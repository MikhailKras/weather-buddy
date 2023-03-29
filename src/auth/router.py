from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import user
from src.auth.schemas import UserCreate, UserResponse
from src.auth.security import get_password_hash
from src.auth.utils import get_user_by_username, get_user_by_email
from src.database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    if await get_user_by_username(user_data.username, session=session):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='This username is already registered!')

    if await get_user_by_email(user_data.email, session=session):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='This email is already registered!')

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
