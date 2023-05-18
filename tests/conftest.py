import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.auth.jwt import get_current_city_data, create_registration_token, is_authenticated
from src.auth.models import user
from src.auth.schemas import UserCreateStep1
from src.config import DB_USER_TEST, DB_PASS_TEST, DB_HOST_TEST, DB_PORT_TEST, DB_NAME_TEST
from src.database import metadata, get_async_session
from src.main import app

DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

engine_test = create_async_engine(DATABASE_URL_TEST)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def city_data():
    return {
        "city": "Brussels",
        "country": "Belgium",
        "latitude": 50.85045,
        "longitude": 4.34878
    }


@pytest.fixture(scope="session")
def registration_token(city_data):
    return create_registration_token(
        city_data["city"],
        city_data["country"],
        city_data["latitude"],
        city_data["longitude"]
    )


@pytest.fixture(scope="session", autouse=True)
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def override_get_current_city_data():
    return UserCreateStep1(
        city="Brussels",
        country="Belgium",
        latitude=50.85045,
        longitude=4.34878
    )


app.dependency_overrides[get_current_city_data] = override_get_current_city_data


@pytest.fixture
async def existing_user():
    async with async_session_maker() as session:
        existing_user_data = {
            "username": "existing_user",
            "email": "existing_user@example.com"
        }
        insert_query = insert(user).values(
            username=existing_user_data["username"],
            email=existing_user_data["email"],
            hashed_password="test",
            city="test",
            country="test",
            latitude=0.0,
            longitude=0.0
        )
        await session.execute(insert_query)
        await session.commit()

        yield existing_user_data
