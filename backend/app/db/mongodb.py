from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import structlog

from app.config import settings

logger = structlog.get_logger()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_mongodb() -> None:
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _db = _client[settings.mongodb_db_name]
    # Verify connection
    await _client.admin.command("ping")
    logger.info("mongodb_connected", db=settings.mongodb_db_name)


async def close_mongodb() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("mongodb_disconnected")


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB is not connected. Call connect_mongodb() first.")
    return _db
