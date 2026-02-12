from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId


SAMPLE_PLAN_DOC = {
    "_id": ObjectId("507f1f77bcf86cd799439033"),
    "name": "Beginner Full Body",
    "description": "Great for beginners",
    "difficulty": "beginner",
    "exercises": [
        {
            "exercise_id": None,
            "name": "Squat",
            "sets": 3,
            "reps": 12,
            "rest_seconds": 60,
            "notes": "Keep back straight",
        },
        {
            "exercise_id": None,
            "name": "Push-up",
            "sets": 3,
            "reps": 10,
            "rest_seconds": 60,
            "notes": "",
        },
    ],
    "estimated_duration_minutes": 45,
    "created_by": "Coach Mike",
    "created_at": datetime(2025, 1, 1),
}

SAMPLE_LOG_DOC = {
    "_id": ObjectId("507f1f77bcf86cd799439044"),
    "member_id": ObjectId("507f1f77bcf86cd799439011"),
    "plan_id": ObjectId("507f1f77bcf86cd799439033"),
    "completed_at": datetime(2025, 2, 1),
    "duration_minutes": 40,
    "exercises_completed": [
        {
            "exercise_name": "Squat",
            "sets_completed": 3,
            "reps_per_set": [12, 12, 10],
            "form_score": 85.0,
        },
    ],
    "source": "manual",
}


class TestWorkoutEndpoints:
    @pytest.mark.asyncio
    async def test_create_plan(self, client, mock_db):
        col = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439033")
        col.insert_one = AsyncMock(return_value=insert_result)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.post(
            "/api/workouts/plans",
            json={
                "name": "Beginner Full Body",
                "description": "Great for beginners",
                "difficulty": "beginner",
                "exercises": [
                    {"name": "Squat", "sets": 3, "reps": 12},
                    {"name": "Push-up", "sets": 3, "reps": 10},
                ],
                "estimated_duration_minutes": 45,
                "created_by": "Coach Mike",
            },
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Beginner Full Body"

    @pytest.mark.asyncio
    async def test_list_plans(self, client, mock_db):
        col = MagicMock()
        col.count_documents = AsyncMock(return_value=1)

        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=[SAMPLE_PLAN_DOC])
        cursor.sort = MagicMock(return_value=cursor)
        col.find = MagicMock(return_value=cursor)

        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/workouts/plans")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_get_plan(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=SAMPLE_PLAN_DOC)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/workouts/plans/507f1f77bcf86cd799439033")
        assert response.status_code == 200
        assert response.json()["name"] == "Beginner Full Body"

    @pytest.mark.asyncio
    async def test_get_plan_not_found(self, client, mock_db):
        col = MagicMock()
        col.find_one = AsyncMock(return_value=None)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.get("/api/workouts/plans/507f1f77bcf86cd799439099")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_log_workout(self, client, mock_db):
        col = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439044")
        col.insert_one = AsyncMock(return_value=insert_result)
        mock_db.__getitem__ = MagicMock(return_value=col)

        response = await client.post(
            "/api/workouts/log",
            json={
                "member_id": "507f1f77bcf86cd799439011",
                "plan_id": "507f1f77bcf86cd799439033",
                "duration_minutes": 40,
                "exercises_completed": [
                    {
                        "exercise_name": "Squat",
                        "sets_completed": 3,
                        "reps_per_set": [12, 12, 10],
                        "form_score": 85.0,
                    },
                ],
                "source": "manual",
            },
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_assign_plan(self, client, mock_db):
        member_col = MagicMock()
        member_col.find_one = AsyncMock(
            return_value={"_id": ObjectId("507f1f77bcf86cd799439011")}
        )

        plan_col = MagicMock()
        plan_col.find_one = AsyncMock(return_value=SAMPLE_PLAN_DOC)

        assign_col = MagicMock()
        assign_col.insert_one = AsyncMock()

        def get_col(name):
            if name == "members":
                return member_col
            elif name == "workout_plans":
                return plan_col
            elif name == "workout_assignments":
                return assign_col
            return MagicMock()

        mock_db.__getitem__ = MagicMock(side_effect=get_col)

        response = await client.post(
            "/api/workouts/assign",
            json={
                "member_id": "507f1f77bcf86cd799439011",
                "plan_id": "507f1f77bcf86cd799439033",
            },
        )

        assert response.status_code == 200
        assert "Plan assigned" in response.json()["message"]
