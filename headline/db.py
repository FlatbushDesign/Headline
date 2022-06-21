from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from fastapi_users.db import BeanieUserDatabase

from headline.config import MONGO_DB_CONNECTION, MONGO_DB_DATABASE
from headline.models import OAuthAccount, User


db: AsyncIOMotorDatabase = None


def connect_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGO_DB_CONNECTION, serverSelectionTimeoutMS=5000)

    global db
    db = client[MONGO_DB_DATABASE]

    return db


def get_collection(name: str) -> AsyncIOMotorCollection:
    global db
    return db[name]


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)
