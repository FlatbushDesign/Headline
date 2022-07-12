from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from fastapi_users.db import BeanieUserDatabase

from headline.config import settings
from headline.models import OAuthAccount, User


db: AsyncIOMotorDatabase = None


def connect_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(
        settings.mongo_db_connection, serverSelectionTimeoutMS=5000
    )

    global db
    db = client[settings.mongo_db_database]

    print(
        f"Connected to DB {settings.mongo_db_database} at {settings.mongo_db_connection.host}"
    )

    return db


def get_collection(name: str) -> AsyncIOMotorCollection:
    global db
    return db[name]


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)
