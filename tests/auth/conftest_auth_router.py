from datetime import datetime

from src.auth.jwt import get_current_city_data, get_current_user
from src.auth.schemas import UserCreateStep1, UserInDB
from src.main import app


def override_get_current_city_data():
    return UserCreateStep1(
        city_id=1
    )


app.dependency_overrides[get_current_city_data] = override_get_current_city_data


async def override_get_current_user():
    return UserInDB(
        id=1,
        username="my_user",
        email="my_user@gmail.com",
        hashed_password="test",
        city_id=1,
        registered_at=datetime.utcnow(),
        disabled=False,
    )


app.dependency_overrides[get_current_user] = override_get_current_user
