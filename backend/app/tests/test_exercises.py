"""Tests for exercise REST API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId


SAMPLE_SESSION_DOC = {
    "_id": ObjectId("507f1f77bcf86cd799439022"),
    "member_id": "507f1f77bcf86cd799439011",
    "exercise": "squat",
    "total_reps": 10,
    "avg_form_score": 85.5,
    "rep_details": [
        {"rep_number": 1, "score": 88.0, "feedback": ["Good depth!"]},
        {"rep_number": 2, "score": 83.0, "feedback": ["Go deeper"]},
    ],
    "duration_seconds": 120,
    "started_at": datetime(2025, 6, 1, 10, 0),
    "ended_at": datetime(2025, 6, 1, 10, 2),
}


class TestExerciseEndpoints:
    @pytest.mark.asyncio
    async def test_list_exercises(self, client, mock_db):
        response = await client.get("/api/exercises")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [e["name"] for e in data]
        assert "squat" in names
        assert "bicep_curl" in names
        assert "shoulder_press" in names

    @pytest.mark.asyncio
    async def test_exercise_has_metadata(self, client, mock_db):
        response = await client.get("/api/exercises")
        data = response.json()
        squat = next(e for e in data if e["name"] == "squat")
        assert squat["display_name"] == "Squat"
        assert "quadriceps" in squat["target_muscles"]
        assert squat["tracked_angle"] == "knee"

    @pytest.mark.asyncio
    async def test_list_sessions(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=1)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[SAMPLE_SESSION_DOC])
        cursor.sort = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/exercises/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["exercise"] == "squat"

    @pytest.mark.asyncio
    async def test_get_session(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=SAMPLE_SESSION_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/exercises/sessions/507f1f77bcf86cd799439022")
        assert response.status_code == 200
        data = response.json()
        assert data["total_reps"] == 10
        assert data["avg_form_score"] == 85.5

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=None)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/exercises/sessions/507f1f77bcf86cd799439099")
        assert response.status_code == 404
