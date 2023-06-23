from datetime import datetime, timedelta
from typing import Optional

from fastapi import status, HTTPException, Depends, Cookie
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import TokenData, UserCreateStep1, UserInDB
from src.auth.utils import get_user_by_username, OAuth2PasswordBearerWithCookie
from src.config import SECRET_KEY, ALGORITHM, SECRET_KEY_REG, SECRET_KEY_EMAIL_VERIFICATION, SECRET_KEY_RESET_PASSWORD
from src.database import get_async_session

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="users/token", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)
) -> UserInDB:
    not_auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token is None:
            raise not_auth_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def is_authenticated(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)
) -> Optional[UserInDB]:
    try:
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    user = await get_user_by_username(token_data.username, session=session)
    return user


def create_registration_token(
        city_id: int,
        expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode = {
        "city_id": city_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_REG, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_city_data(
        registration_token: Optional[str] = Cookie(None)
) -> UserCreateStep1:
    try:
        if registration_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Registration token not found")
        payload = jwt.decode(registration_token, SECRET_KEY_REG, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid registration token")
    return UserCreateStep1(**payload)


def create_email_verification_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode = {"email": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_EMAIL_VERIFICATION, algorithm=ALGORITHM)
    return encoded_jwt


def get_email_from_token(token: str) -> str:
    try:
        if token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
        payload = jwt.decode(token, SECRET_KEY_EMAIL_VERIFICATION, algorithms=ALGORITHM)
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return email


def create_reset_password_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_RESET_PASSWORD, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_id_from_token(token: str) -> int:
    try:
        if token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
        payload = jwt.decode(token, SECRET_KEY_RESET_PASSWORD, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user_id
