from datetime import datetime

from src.auth.jwt import get_current_city_data, get_current_user
from src.auth.schemas import UserCreateStep1, UserInDB
from src.main import app


def override_get_current_city_data():
    return UserCreateStep1(
        city="Brussels",
        country="Belgium",
        latitude=50.85045,
        longitude=4.34878
    )


app.dependency_overrides[get_current_city_data] = override_get_current_city_data


async def override_get_current_user():
    return UserInDB(
        id=1,
        username="my_user",
        email="my_user@gmail.com",
        hashed_password="test",
        registered_at=datetime.utcnow(),
        disabled=False,
        city="Brussels",
        country="Belgium",
        latitude=50.85045,
        longitude=4.34878
    )


app.dependency_overrides[get_current_user] = override_get_current_user
