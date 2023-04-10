from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_access_token
from src.auth.models import user
from src.auth.schemas import UserCreate, UserResponse, Token
from src.auth.security import get_password_hash
from src.auth.utils import get_user_by_username, get_user_by_email, authenticate_user
from src.database import get_async_session

ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

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


@router.post('/token', response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    user_data = await authenticate_user(form_data, session=session)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
