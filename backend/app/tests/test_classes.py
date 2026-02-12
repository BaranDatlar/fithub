from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId


SAMPLE_CLASS_DOC = {
    "_id": ObjectId("507f1f77bcf86cd799439022"),
    "name": "Morning Yoga",
    "description": "Relaxing morning yoga session",
    "instructor": "Sarah",
    "category": "yoga",
    "schedule": {
        "day_of_week": 1,
        "start_time": "09:00",
        "end_time": "10:00",
        "recurring": True,
    },
    "capacity": 20,
    "current_bookings": 5,
    "participants": [ObjectId("507f1f77bcf86cd799439011")],
    "location": "Studio A",
    "status": "scheduled",
    "created_at": datetime(2025, 1, 1),
}


class TestClassEndpoints:

    @pytest.mark.asyncio
    async def test_create_class(self, client, mock_db):
        col = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439022")
        col.insert_one = AsyncMock(return_value=insert_result)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.post("/api/classes", json={
            "name": "Morning Yoga",
            "description": "Relaxing morning yoga session",
            "instructor": "Sarah",
            "category": "yoga",
            "schedule": {
                "day_of_week": 1,
                "start_time": "09:00",
                "end_time": "10:00",
                "recurring": True,
            },
            "capacity": 20,
            "location": "Studio A",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Morning Yoga"
        assert data["capacity"] == 20

    @pytest.mark.asyncio
    async def test_list_classes(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=1)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[SAMPLE_CLASS_DOC])
        cursor.sort = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/classes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_class(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=SAMPLE_CLASS_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/classes/507f1f77bcf86cd799439022")
        assert response.status_code == 200
        assert response.json()["name"] == "Morning Yoga"

    @pytest.mark.asyncio
    async def test_get_class_not_found(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=None)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/classes/507f1f77bcf86cd799439099")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_book_class(self, client, mock_db, mock_redis):
        col = MagicMock()
        # First call: capacity check (find_one for class)
        # Second call: check if already booked
        col.find_one = AsyncMock(side_effect=[
            SAMPLE_CLASS_DOC,  # class exists for capacity init
            None,               # member not already booked
        ])
        col.update_one = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=col)

        # Redis: capacity not cached, then decrement returns > 0
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()
        mock_redis.decr = AsyncMock(return_value=14)

        response = await client.post(
            "/api/classes/507f1f77bcf86cd799439022/book?member_id=507f1f77bcf86cd799439011"
        )

        assert response.status_code == 200
        assert "spots_left" in response.json()

    @pytest.mark.asyncio
    async def test_delete_class(self, client, mock_db):
        col = MagicMock()
        col.find_one_and_update = AsyncMock(return_value=SAMPLE_CLASS_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.delete("/api/classes/507f1f77bcf86cd799439022")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_list_classes_with_filters(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=0)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[])
        cursor.sort = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/classes?category=yoga&day_of_week=1")
        assert response.status_code == 200
