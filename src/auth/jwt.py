from datetime import datetime, timedelta

from fastapi import status, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import TokenData
from src.auth.utils import get_user_by_username, OAuth2PasswordBearerWithCookie
from src.config import SECRET_KEY, ALGORITHM
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
):
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
) -> bool:
    try:
        if token is None:
            return False
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return False
        token_data = TokenData(username=username)
    except JWTError:
        return False
    user = await get_user_by_username(token_data.username, session=session)
    return bool(user)
