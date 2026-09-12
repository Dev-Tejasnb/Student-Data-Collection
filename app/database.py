from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncMongoClient = None
    db: AsyncDatabase = None


db = Database()


async def connect_to_mongo():
    settings = get_settings()
    try:
        db.client = AsyncMongoClient(settings.MONGODB_URI)
        db.db = db.client[settings.DATABASE_NAME]
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
        await create_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    if db.client:
        await db.client.close()
        logger.info("Closed MongoDB connection")


async def get_database() -> AsyncDatabase:
    return db.db


async def create_indexes():
    database = await get_database()

    await database.students.create_index("created_at")
    await database.students.create_index("name")
    await database.students.create_index("college")
    await database.students.create_index("course")
    await database.students.create_index("admission_through")

    await database.users.create_index("username", unique=True)

    logger.info("Database indexes created")