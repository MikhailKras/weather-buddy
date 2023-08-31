from typing import AsyncGenerator

import motor.motor_asyncio
from redis import asyncio as aioredis
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, MONGODB_NAME, MONGODB_URL, REDIS_HOST, REDIS_PORT

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()

metadata = MetaData()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class MongoDB:
    def __init__(self, mongodb_url, db_name):
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.db = None
        self.client = None

    async def connect(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
        self.db = self.client[self.db_name]

    async def disconnect(self):
        if self.client:
            self.client.close()


mongo_db = MongoDB(mongodb_url=MONGODB_URL, db_name=MONGODB_NAME)


class RedisDB:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, encoding="utf8", decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()


redis_db = RedisDB(redis_url=f"redis://{REDIS_HOST}:{REDIS_PORT}")
