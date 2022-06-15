from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from headline.config import MONGO_DB_CONNECTION, MONGO_DB_DATABASE


db: AsyncIOMotorDatabase = None


def connect_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGO_DB_CONNECTION, serverSelectionTimeoutMS=5000)

    global db
    db = client[MONGO_DB_DATABASE]


def get_collection(name: str) -> AsyncIOMotorCollection:
    global db
    return db[name]
