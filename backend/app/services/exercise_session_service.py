"""
Exercise Session Service — persists completed exercise sessions to MongoDB
and publishes events to Kafka.
"""

from datetime import datetime

from bson import ObjectId

import structlog

from app.db.mongodb import get_database
from app.models.exercise import ExerciseSessionResponse
from app.services.kafka_service import publish_event, TOPICS

logger = structlog.get_logger()


class ExerciseSessionService:
    COLLECTION = "exercise_sessions"

    @staticmethod
    async def save_session(
        member_id: str,
        exercise: str,
        total_reps: int,
        avg_form_score: float | None,
        rep_details: list[dict],
        duration_seconds: int,
        started_at: datetime,
    ) -> ExerciseSessionResponse:
        db = get_database()
        doc = {
            "member_id": member_id,
            "exercise": exercise,
            "total_reps": total_reps,
            "avg_form_score": avg_form_score,
            "rep_details": rep_details,
            "duration_seconds": duration_seconds,
            "started_at": started_at,
            "ended_at": datetime.utcnow(),
        }
        result = await db[ExerciseSessionService.COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id

        await publish_event(
            topic=TOPICS["exercise_events"],
            event_type="exercise.session_completed",
            data={
                "session_id": str(result.inserted_id),
                "member_id": member_id,
                "exercise": exercise,
                "total_reps": total_reps,
                "avg_form_score": avg_form_score,
                "duration_seconds": duration_seconds,
            },
            key=member_id,
        )

        logger.info(
            "exercise_session_saved",
            session_id=str(result.inserted_id),
            exercise=exercise,
            reps=total_reps,
        )

        return ExerciseSessionResponse.from_mongo(doc)

    @staticmethod
    async def list_sessions(
        member_id: str | None = None, exercise: str | None = None, limit: int = 20
    ) -> dict:
        db = get_database()
        query: dict = {}
        if member_id:
            query["member_id"] = member_id
        if exercise:
            query["exercise"] = exercise

        total = await db[ExerciseSessionService.COLLECTION].count_documents(query)
        cursor = (
            db[ExerciseSessionService.COLLECTION]
            .find(query)
            .sort("started_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)

        return {
            "items": [ExerciseSessionResponse.from_mongo(d) for d in docs],
            "total": total,
        }

    @staticmethod
    async def get_session(session_id: str) -> ExerciseSessionResponse | None:
        db = get_database()
        doc = await db[ExerciseSessionService.COLLECTION].find_one(
            {"_id": ObjectId(session_id)}
        )
        if not doc:
            return None
        return ExerciseSessionResponse.from_mongo(doc)
