from datetime import datetime

from bson import ObjectId
import structlog

from app.db.mongodb import get_database
from app.services.kafka_service import create_consumer, TOPICS
from app.services.redis_service import RedisService

logger = structlog.get_logger()


class WorkoutSummaryWorker:
    """
    Listens to exercise.session_completed events and creates workout log entries.
    Bridges AI exercise tracker data with the workout logging system.
    """

    def __init__(self):
        self.consumer = create_consumer(
            topics=[TOPICS["exercise_events"]],
            group_id="workout_summary_consumer",
        )

    async def run(self):
        await self.consumer.start()
        logger.info("workout_summary_worker_started")

        try:
            async for message in self.consumer:
                try:
                    event = message.value
                    event_type = event.get("event_type")

                    if event_type == "exercise.session_completed":
                        await self._handle_session_completed(event)

                except Exception as e:
                    logger.error("workout_summary_error", error=str(e))
        finally:
            await self.consumer.stop()

    async def _handle_session_completed(self, event: dict):
        db = get_database()

        member_id = event.get("member_id")
        if not member_id:
            return

        workout_log = {
            "member_id": ObjectId(member_id),
            "plan_id": None,
            "completed_at": datetime.utcnow(),
            "duration_minutes": max(1, event.get("duration_seconds", 60) // 60),
            "exercises_completed": [
                {
                    "exercise_name": event.get("exercise", "unknown"),
                    "sets_completed": 1,
                    "reps_per_set": [event.get("total_reps", 0)],
                    "form_score": event.get("avg_form_score"),
                }
            ],
            "source": "ai_tracker",
        }

        await db["workout_logs"].insert_one(workout_log)

        # Invalidate analytics cache
        await RedisService.invalidate("analytics:overview")

        logger.info(
            "workout_log_created_from_ai",
            member_id=member_id,
            exercise=event.get("exercise"),
            reps=event.get("total_reps"),
            avg_score=event.get("avg_form_score"),
        )
