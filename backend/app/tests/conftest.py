from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def mock_db():
    """Mock MongoDB database with collection methods."""
    db = MagicMock()

    # Create async mock collection
    def make_collection():
        col = AsyncMock()
        col.find_one = AsyncMock(return_value=None)
        col.insert_one = AsyncMock()
        col.find_one_and_update = AsyncMock(return_value=None)
        col.count_documents = AsyncMock(return_value=0)
        col.update_one = AsyncMock()

        # Mock cursor chain: find().sort().skip().limit().to_list()
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[])
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        # Mock aggregation
        agg_cursor = AsyncMock()
        agg_cursor.to_list = AsyncMock(return_value=[])
        col.aggregate = MagicMock(return_value=agg_cursor)

        return col

    db.__getitem__ = MagicMock(side_effect=lambda name: make_collection())
    return db


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.incr = AsyncMock(return_value=1)
    redis.decr = AsyncMock(return_value=1)
    redis.ping = AsyncMock()
    redis.scan_iter = MagicMock(return_value=iter([]))
    return redis


@pytest.fixture
def mock_kafka():
    """Mock Kafka producer."""
    producer = AsyncMock()
    producer.send = AsyncMock()
    return producer


@pytest.fixture
async def client(mock_db, mock_redis, mock_kafka):
    """Async test client with all dependencies mocked."""
    with (
        # Patch at every module that imports get_database / get_redis
        patch("app.services.member_service.get_database", return_value=mock_db),
        patch("app.services.class_service.get_database", return_value=mock_db),
        patch("app.services.workout_service.get_database", return_value=mock_db),
        patch("app.services.analytics_service.get_database", return_value=mock_db),
        patch("app.services.redis_service.get_redis", return_value=mock_redis),
        patch("app.services.kafka_service._producer", mock_kafka),
        # Patch lifespan connections
        patch("app.main.connect_mongodb", new_callable=AsyncMock),
        patch("app.main.close_mongodb", new_callable=AsyncMock),
        patch("app.main.connect_redis", new_callable=AsyncMock),
        patch("app.main.close_redis", new_callable=AsyncMock),
        patch("app.main.start_producer", new_callable=AsyncMock),
        patch("app.main.stop_producer", new_callable=AsyncMock),
        # Patch health check imports
        patch("app.db.mongodb.get_database", return_value=mock_db),
        patch("app.db.redis.get_redis", return_value=mock_redis),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
