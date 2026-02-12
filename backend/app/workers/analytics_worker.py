import structlog

from app.services.kafka_service import create_consumer, TOPICS
from app.services.redis_service import RedisService

logger = structlog.get_logger()


class AnalyticsWorker:
    """
    Listens to all event topics and invalidates analytics caches.
    This ensures dashboard data stays fresh after any change.
    """

    def __init__(self):
        self.consumer = create_consumer(
            topics=[
                TOPICS["member_events"],
                TOPICS["class_events"],
                TOPICS["workout_events"],
                TOPICS["exercise_events"],
            ],
            group_id="analytics_consumer",
        )

    async def run(self):
        await self.consumer.start()
        logger.info("analytics_worker_started")

        try:
            async for message in self.consumer:
                try:
                    event = message.value
                    event_type = event.get("event_type", "unknown")
                    topic = message.topic

                    logger.info(
                        "analytics_event_received",
                        topic=topic,
                        event_type=event_type,
                    )

                    # Invalidate relevant caches based on event type
                    await self._invalidate_caches(topic, event_type)

                except Exception as e:
                    logger.error("analytics_worker_error", error=str(e))
        finally:
            await self.consumer.stop()

    async def _invalidate_caches(self, topic: str, event_type: str):
        # Always invalidate overview
        await RedisService.invalidate("analytics:overview")

        if topic == TOPICS["member_events"]:
            await RedisService.invalidate("analytics:members")
            await RedisService.invalidate("analytics:member_count")
            await RedisService.invalidate("analytics:revenue")

        elif topic == TOPICS["class_events"]:
            await RedisService.invalidate("analytics:classes")

        elif topic in (TOPICS["workout_events"], TOPICS["exercise_events"]):
            # Workout-related events don't need member/class cache invalidation
            pass

        logger.info("cache_invalidated", topic=topic, event_type=event_type)
