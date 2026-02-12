from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId


SAMPLE_MEMBER_DOC = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+31612345678",
    "membership": {
        "plan": "premium",
        "status": "active",
        "start_date": datetime(2025, 1, 1),
        "end_date": None,
    },
    "profile": {
        "age": 28,
        "weight": 80.0,
        "height": 180.0,
        "fitness_level": "intermediate",
        "goals": ["muscle_gain", "endurance"],
    },
    "created_at": datetime(2025, 1, 1),
    "updated_at": datetime(2025, 1, 1),
    "is_deleted": False,
}


class TestMemberEndpoints:

    @pytest.mark.asyncio
    async def test_create_member(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=None)  # no duplicate
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        col.insert_one = AsyncMock(return_value=insert_result)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.post("/api/members", json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+31612345678",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["email"] == "john@example.com"

    @pytest.mark.asyncio
    async def test_create_member_duplicate_email(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=SAMPLE_MEMBER_DOC)  # exists
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.post("/api/members", json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "john@example.com",
        })

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_list_members(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=1)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[SAMPLE_MEMBER_DOC])
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/members")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_get_member(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=SAMPLE_MEMBER_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/members/507f1f77bcf86cd799439011")
        assert response.status_code == 200
        assert response.json()["first_name"] == "John"

    @pytest.mark.asyncio
    async def test_get_member_not_found(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=None)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/members/507f1f77bcf86cd799439099")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_member(self, client, mock_db):
        updated_doc = {**SAMPLE_MEMBER_DOC, "first_name": "Jonathan"}
        col = MagicMock()
        col.find_one_and_update = AsyncMock(return_value=updated_doc)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.put(
            "/api/members/507f1f77bcf86cd799439011",
            json={"first_name": "Jonathan"},
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Jonathan"

    @pytest.mark.asyncio
    async def test_delete_member(self, client, mock_db):
        col = MagicMock()
        col.find_one_and_update = AsyncMock(return_value=SAMPLE_MEMBER_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.delete("/api/members/507f1f77bcf86cd799439011")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_list_members_with_search(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=1)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[SAMPLE_MEMBER_DOC])
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/members?search=john")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_members_with_filters(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=0)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[])
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/members?status=active&plan=premium")
        assert response.status_code == 200
