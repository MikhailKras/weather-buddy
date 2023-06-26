import time
from datetime import timedelta
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_access_token, get_current_user, is_authenticated, create_registration_token, get_current_city_data, \
    create_email_verification_token, get_email_from_token, create_reset_password_token, get_user_id_from_token
from src.auth.models import user, email_verification
from src.auth.schemas import UserCreateStep2, Token, UserInDB, UserUpdateData, PasswordChange, UserCreateStep1, UserUpdateCity, \
    UserEmailVerificationInfo, EmailPasswordReset, PasswordReset, CityNameSearchHistoryPresentation, CoordinatesSearchHistoryPresentation
from src.auth.security import get_password_hash, verify_password
from src.auth.tasks import task_send_reset_password_mail, task_send_verification_code
from src.auth.utils import get_user_by_username, get_user_by_email, authenticate_user, get_user_email_verification_info, get_user_city_data, \
    get_user_by_user_id, get_search_history_data
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, CLIENT_ORIGIN
from src.database import get_async_session
from src.rate_limiter.callback import custom_callback
from src.weather_service.schemas import CityInDB
from src.weather_service.utils import search_cities_db

router = APIRouter(
    prefix='/users',
    tags=['Auth']
)

templates = Jinja2Templates(directory='src/templates')


@router.get('/register/city', response_class=HTMLResponse)
async def register_step_1(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    if user_data:
        return RedirectResponse('/users/me')
    return templates.TemplateResponse('auth/register_step_1_city.html', context={"request": request})


@router.get('/{purpose}/city/choose_city_name', response_class=HTMLResponse)
async def find_city_name_matches(
        request: Request,
        purpose: str,
        city_input: str,
        session: AsyncSession = Depends(get_async_session),
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    if purpose not in ('register', 'settings'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid purpose!')
    city_info: List[CityInDB] = await search_cities_db(city_input.title(), session=session)
    if not city_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid city!')
    data = {
        "cities": [
            {
                "name": city_info[x].name,
                "country": city_info[x].country,
                "region": city_info[x].region,
                "latitude": city_info[x].latitude,
                "longitude": city_info[x].longitude,
                "id": city_info[x].id
            }
            for x in range(len(city_info))
        ]
    }
    return templates.TemplateResponse(
        'auth/choose_city_name.html', context={"request": request, "data": data, "is_auth": user_data, "purpose": purpose}
    )


@router.post('/register/city', response_class=RedirectResponse)
async def register_step_1_submit(
        city_data: UserCreateStep1
):
    registration_token = create_registration_token(city_data.city_id)
    redirect_url = '/users/register/details'
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="registration_token", value=registration_token, httponly=True, max_age=600)
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
        city_id=city_data.city_id
    ).returning(user.c.id)

    result = await session.execute(insert_query)
    await session.commit()

    inserted_row = result.fetchone()
    user_id = inserted_row.id

    verification_token = create_email_verification_token(user_data.email)

    insert_verification_query = insert(email_verification).values(
        user_id=user_id,
        token=verification_token
    )

    await session.execute(insert_verification_query)
    await session.commit()

    url = f"{CLIENT_ORIGIN}/users/verify-email-page/{verification_token}"
    task_send_verification_code.delay(user_data.username, url, [user_data.email])

    return {'message': 'Registration successful. Please verify your email to gain full access.'}


@router.get("/register/success", response_class=HTMLResponse)
async def register_success(request: Request, message: str):
    response = templates.TemplateResponse("auth/registration_success.html", {"request": request, "message": message})
    response.delete_cookie(key="registration_token")
    return response


@router.get('/verify-email-page/{token}')
async def verify_email_page(
        request: Request,
        token: str,
        user_data: Optional[UserInDB] = Depends(is_authenticated)
):
    return templates.TemplateResponse("auth/email_verification.html", {"request": request, "token": token, "is_auth": user_data})


@router.get('/verify-email/{token}', dependencies=[Depends(RateLimiter(times=5, seconds=60, callback=custom_callback))])
async def verify_email(
        token: str,
        session: AsyncSession = Depends(get_async_session)
):
    email = get_email_from_token(token)

    select_verification_query = select(email_verification).where(email_verification.c.token == token)
    existing_verification = await session.execute(select_verification_query)
    verification = existing_verification.fetchone()

    if verification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email verification token not found"
        )

    if verification.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    user_data = await get_user_by_email(email, session=session)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_verification_query = update(email_verification).where(email_verification.c.token == token).values(
        verified=True
    )

    await session.execute(update_verification_query)
    await session.commit()

    return {"message": "Email verification successful"}


@router.get('/email-verification')
async def get_send_verification_email_page(request: Request):
    return templates.TemplateResponse("auth/send_email_verification.html", {"request": request})


@router.post('/email-verification', dependencies=[Depends(RateLimiter(times=5, seconds=60, callback=custom_callback))])
async def send_verification_email(
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    user_email_verification_info: UserEmailVerificationInfo = await get_user_email_verification_info(user_data.id, session=session)

    if user_email_verification_info.verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already verified")

    verification_token = create_email_verification_token(user_data.email)

    update_query = update(email_verification).where(email_verification.c.user_id == user_data.id).values(
        token=verification_token
    )

    await session.execute(update_query)
    await session.commit()

    url = f"{CLIENT_ORIGIN}/users/verify-email-page/{verification_token}"

    try:
        task_send_verification_code.delay(user_data.username, url, [user_data.email])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to send verification email. Please try again later.")

    return {"message": "Verification email sent successfully"}


@router.get('/login', response_class=HTMLResponse)
async def login_user_get_form(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    if user_data:
        return RedirectResponse('/users/me')
    response = templates.TemplateResponse('auth/login.html', context={"request": request})
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
    cookie_max_age = int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=cookie_max_age)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_class=HTMLResponse)
async def read_users_me(
        request: Request,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    user_city_data: CityInDB = await get_user_city_data(user_data.city_id, session=session)
    user_email_verification_info: UserEmailVerificationInfo = await get_user_email_verification_info(user_data.id, session=session)
    personal_data = {
        'username': user_data.username,
        'email': user_data.email,
        'is email verified': user_email_verification_info.verified,
        'registered at': user_data.registered_at.strftime("%B %d, %Y at %H:%M, UTC time"),
    }
    city_data = {
        'city': user_city_data.name,
        'region': user_city_data.region,
        'country': user_city_data.country,
        'population': user_city_data.population,
        'latitude': round(user_city_data.latitude, 2),
        'longitude': round(user_city_data.longitude, 2),
    }
    return templates.TemplateResponse('auth/user_data.html', context={
        "request": request,
        "personal_data": personal_data,
        "city_data": city_data
    })


@router.get("/logout", response_class=RedirectResponse)
async def logout(user_data: Optional[UserInDB] = Depends(is_authenticated)):
    response = RedirectResponse("/users/login")
    if user_data:
        response.delete_cookie(key="access_token")
    return response


@router.get("/settings", response_class=HTMLResponse)
async def get_account_settings(
        request: Request,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    user_city_data: CityInDB = await get_user_city_data(user_data.city_id, session=session)
    data = {
        'username': user_data.username,
        'email': user_data.email,
        'city': user_city_data.name,
        'region': user_city_data.region,
        'country': user_city_data.country,
        'population': user_city_data.population,
        'latitude': user_city_data.latitude,
        'longitude': user_city_data.longitude,
        'registered_at': user_data.registered_at.strftime("%B %d, %Y at %I:%M %p"),
    }
    return templates.TemplateResponse('auth/settings.html', context={"request": request, "user_data": data})


@router.patch("/settings/update_data", status_code=status.HTTP_200_OK)
async def update_user_data(
        response: Response,
        new_data: UserUpdateData,
        current_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    if (new_data.username, new_data.email) == (current_data.username, current_data.email):
        raise HTTPException(status_code=400, detail="No changes detected")

    async def update_user_field(field_name: str):
        current_value, new_value = getattr(current_data, field_name), getattr(new_data, field_name)
        if current_value != new_value:
            if field_name == 'username':
                if await get_user_by_username(new_value, session=session):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        detail='This username is already registered!')
                new_access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
                new_access_token = create_access_token(data={"sub": new_data.username}, expires_delta=new_access_token_expires)
                cookie_max_age = int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60
                response.set_cookie(key='access_token', value=f"Bearer {new_access_token}", httponly=True, max_age=cookie_max_age)
            elif field_name == 'email':
                if await get_user_by_email(new_value, session=session):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        detail='This email is already registered!')
                update_verification_query = update(email_verification).where(email_verification.c.user_id == current_data.id).values(
                    verified=False
                )
                await session.execute(update_verification_query)
            update_query = update(user).where(user.c.username == current_data.username).values(**{field_name: new_value})
            await session.execute(update_query)
            await session.commit()

    for field in new_data.__fields__:
        await update_user_field(field)

    return {"message": "Data changed successfully!"}


@router.patch("/settings/change_city_data")
async def change_city_data(
        city_data: UserUpdateCity,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):

    if city_data.city_id == user_data.city_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City already chosen"
        )

    update_query = update(user).where(user.c.username == user_data.username).values(
        city_id=city_data.city_id
    )

    await session.execute(update_query)
    await session.commit()

    return {"message": "City changed successfully!"}


@router.patch("/settings/change_password", status_code=status.HTTP_200_OK)
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

    return {"message": "Password changed successfully!"}


@router.delete("/settings/delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        response: Response,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    user_id = user_data.id

    delete_verification_query = delete(email_verification).where(email_verification.c.user_id == user_id)
    await session.execute(delete_verification_query)

    delete_user_query = delete(user).where(user.c.id == user_id)
    await session.execute(delete_user_query)

    await session.commit()

    response.delete_cookie("access_token")


@router.get("/my_city_info", response_class=RedirectResponse)
async def get_my_city_info(
    user_data: UserInDB = Depends(get_current_user),
):
    url = f"/weather/info?city_id={user_data.city_id}"
    response = RedirectResponse(url)

    return response


@router.get("/password-reset", response_class=HTMLResponse)
async def get_password_reset_page_with_email(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    if user_data:
        return RedirectResponse('/users/me')
    return templates.TemplateResponse('auth/reset_password/get_email.html', context={"request": request})


@router.post("/password-reset", dependencies=[Depends(RateLimiter(times=5, seconds=30, callback=custom_callback))])
async def post_email_for_password_reset(
        email_data: EmailPasswordReset,
        session: AsyncSession = Depends(get_async_session),
):
    user_data = await get_user_by_email(email_data.email, session=session)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_email_verification_info = await get_user_email_verification_info(user_data.id, session=session)

    if not user_email_verification_info.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Email not verified")

    reset_password_token = create_reset_password_token(user_data.id)
    url = f"{CLIENT_ORIGIN}/users/password-reset/form/{reset_password_token}"

    try:
        task_send_reset_password_mail.delay(user_data.username, url, [user_data.email])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to send reset password email. Please try again later.")

    return {"message": "Reset password email sent successfully"}


@router.get("/password-reset/form/{token}")
async def get_password_reset_page_with_passwords(
        request: Request,
        token: str
):
    user_id = get_user_id_from_token(token)
    if user_id:
        return templates.TemplateResponse("auth/reset_password/get_passwords.html", {"request": request, "token": token})


@router.patch("/password-reset/update/{token}")
async def reset_password(
        token: str,
        password_reset: PasswordReset,
        session: AsyncSession = Depends(get_async_session),
):
    user_id = get_user_id_from_token(token)

    user_data = await get_user_by_user_id(user_id, session=session)

    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_query = update(user).where(user.c.id == user_id).values(
        hashed_password=get_password_hash(password_reset.password)
    )
    await session.execute(update_query)
    await session.commit()

    return {"message": "Password updated successfully"}


@router.get("/search_history_data")
async def get_search_data(
        request: Request,
        user_data: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    city_name_search_history_data, coordinates_search_history_data = await get_search_history_data(user_id=user_data.id, session=session)
    presentation_data = {
        "city_name_search_history_data": [],
        "coordinates_search_history_data": []
    }

    if city_name_search_history_data:
        for row in city_name_search_history_data:
            search_time = row.request_at.strftime("%d/%m/%y %H:%M:%S")
            city_data: CityInDB = await get_user_city_data(row.city_id, session=session)
            search_history_presentation = CityNameSearchHistoryPresentation(
                city_id=row.city_id,
                city_name=city_data.name,
                region=city_data.region,
                country=city_data.country,
                latitude=city_data.latitude,
                longitude=city_data.longitude,
                search_time=search_time
            )
            presentation_data["city_name_search_history_data"].append(search_history_presentation)

    if coordinates_search_history_data:
        for row in coordinates_search_history_data:
            search_time = row.request_at.strftime("%d/%m/%y %H:%M:%S")
            search_history_presentation = CoordinatesSearchHistoryPresentation(
                place_name=row.place_name,
                region=row.region,
                country=row.country,
                latitude=row.latitude,
                longitude=row.longitude,
                search_time=search_time
            )
            presentation_data["coordinates_search_history_data"].append(search_history_presentation)

    return templates.TemplateResponse("auth/search_data.html", {
        "request": request,
        "search_history_presentation_data": presentation_data
    })
