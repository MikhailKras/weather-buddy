from datetime import timedelta

import geonamescache
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_access_token, get_current_user, is_authenticated, create_registration_token, get_current_city_data
from src.auth.models import user
from src.auth.schemas import UserCreateStep2, UserResponse, Token, UserInDB, UserUpdate, PasswordChange, UserCreateStep1
from src.auth.security import get_password_hash, verify_password
from src.auth.utils import get_user_by_username, get_user_by_email, authenticate_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)

templates = Jinja2Templates(directory='src/templates')


@router.get('/register/city', response_class=HTMLResponse)
async def register_step_1(request: Request, is_auth: bool = Depends(is_authenticated)):
    if is_auth:
        return RedirectResponse('/users/me')
    return templates.TemplateResponse('auth/register_step_1_city.html', context={"request": request})


@router.get('/register/city/choose_city_name', response_class=HTMLResponse)
async def find_city_name_matches(request: Request, city_input: str, is_auth: bool = Depends(is_authenticated)):
    gc = geonamescache.GeonamesCache()
    city_info = gc.search_cities(city_input.title())
    if not city_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
    city_names = [city_info[x]['name'] for x in range(len(city_info))]
    country_codes = [city_info[x]['countrycode'] for x in range(len(city_info))]
    countries_info: dict = gc.get_countries()
    country_names = [countries_info.get(country_code)['name'] for country_code in country_codes]
    coordinates = [{'latitude': city_info[x]['latitude'], 'longitude': city_info[x]['longitude']} for x in range(len(city_info))]
    data = {'cities': [{'name': name, 'country': country, 'coordinates': coords} for name, country, coords in zip(city_names, country_names, coordinates)]}
    return templates.TemplateResponse(
        'auth/choose_city_name.html', context={"request": request, "data": data, "is_auth": is_auth}
    )


@router.post('/register/city', response_class=RedirectResponse)
async def register_step_1_submit(
        city_data: UserCreateStep1
):
    registration_token = create_registration_token(city_data.city, city_data.country)
    redirect_url = '/users/register/details'
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="registration_token", value=registration_token, httponly=True)
    return response


@router.get('/register/details', response_class=HTMLResponse)
async def register_step_2(request: Request):
    registration_token = request.cookies.get("registration_token")
    if registration_token is None:
        return RedirectResponse('/users/register/city')
    return templates.TemplateResponse('auth/register_step_2_user_data.html', {'request': request})


@router.post('/register/details', status_code=status.HTTP_201_CREATED)
async def register_step_2_submit(
        user_data: UserCreateStep2,
        city_data: UserCreateStep1 = Depends(get_current_city_data),
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
        city=city_data.city,
        country=city_data.country
    )

    await session.execute(insert_query)
    await session.commit()

    return {'message': 'Registration successful'}


@router.get('/login', response_class=HTMLResponse)
async def login_user_get_form(request: Request, is_auth: bool = Depends(is_authenticated)):
    if is_auth:
        return RedirectResponse('/users/me')
    response = templates.TemplateResponse('auth/login.html', context={"request": request})
    response.delete_cookie(key="registration_token")
    return response


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


@router.patch("/settings/update_data", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user_data(
        response: Response,
        new_data: UserUpdate,
        current_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
) -> UserResponse:

    async def update_user_field(field_name: str):
        current_value, new_value = getattr(current_data, field_name), getattr(new_data, field_name)
        if current_value != new_value:
            if field_name == 'username':
                if await get_user_by_username(new_value, session=session):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        detail='This username is already registered!')
                new_access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
                new_access_token = create_access_token(data={"sub": new_data.username}, expires_delta=new_access_token_expires)
                response.set_cookie(key='access_token', value=f"Bearer {new_access_token}", httponly=True)
            elif field_name == 'email':
                if await get_user_by_email(new_value, session=session):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        detail='This email is already registered!')
            update_query = update(user).where(user.c.username == current_data.username).values(**{field_name: new_value})
            await session.execute(update_query)
            await session.commit()

    for field in new_data.__fields__:
        await update_user_field(field)

    return UserResponse(**new_data.dict())


@router.patch("/settings/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
        passwords: PasswordChange,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    if not verify_password(passwords.current_password, user_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Current password is incorrect')
    update_query = update(user).where(user.c.username == user_data.username).values(
        hashed_password=get_password_hash(passwords.new_password)
    )
    await session.execute(update_query)
    await session.commit()


@router.delete("/settings/delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        response: Response,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    delete_query = delete(user).where(user.c.username == user_data.username)
    await session.execute(delete_query)
    await session.commit()

    response.delete_cookie("access_token")
