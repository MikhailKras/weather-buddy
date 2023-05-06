from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_access_token, get_current_user, is_authenticated
from src.auth.models import user
from src.auth.schemas import UserCreate, UserResponse, Token, UserInDB
from src.auth.security import get_password_hash
from src.auth.utils import get_user_by_username, get_user_by_email, authenticate_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)

templates = Jinja2Templates(directory='src/templates')


@router.get('/register', response_class=HTMLResponse)
async def register_user_get_form(request: Request, is_auth: bool = Depends(is_authenticated)):
    if is_auth:
        return RedirectResponse('/users/me')
    return templates.TemplateResponse('auth/register.html', context={"request": request})


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session)
) -> dict[str, str]:
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


@router.get('/login', response_class=HTMLResponse)
async def login_user_get_form(request: Request, is_auth: bool = Depends(is_authenticated)):
    if is_auth:
        return RedirectResponse('/users/me')
    return templates.TemplateResponse('auth/login.html', context={"request": request})


@router.post('/token', response_model=Token)
async def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
) -> dict[str, str]:
    user_data = await authenticate_user(form_data, session=session)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={'sub': user_data.username}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_class=HTMLResponse)
async def read_users_me(
        request: Request,
        user_data: UserInDB = Depends(get_current_user)
):
    data = {
        'username': user_data.username,
        'email': user_data.email,
        'city': user_data.city,
        'registered_at': user_data.registered_at.strftime("%B %d, %Y at %I:%M %p")
    }
    return templates.TemplateResponse('auth/user_data.html', context={"request": request, "user_data": data})


@router.get("/logout", response_class=RedirectResponse)
async def logout(is_auth: bool = Depends(is_authenticated)):
    response = RedirectResponse("/users/login")
    if is_auth:
        response.delete_cookie(key="access_token")
    return response


@router.get("/settings", response_class=HTMLResponse)
async def get_account_settings(
        request: Request,
        user_data: UserInDB = Depends(get_current_user)
):
    data = {
        'username': user_data.username,
        'email': user_data.email,
        'city': user_data.city,
        'registered_at': user_data.registered_at.strftime("%B %d, %Y at %I:%M %p")
    }
    return templates.TemplateResponse('auth/settings.html', context={"request": request, "user_data": data})
