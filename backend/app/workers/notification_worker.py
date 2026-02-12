import structlog

from app.services.kafka_service import create_consumer, TOPICS

logger = structlog.get_logger()


class NotificationWorker:
    """
    Listens to class events and logs notifications.
    In production, this would send push notifications, emails, etc.
    For MVP, it logs events to console (demonstrates the pattern).
    """

    def __init__(self):
        self.consumer = create_consumer(
            topics=[TOPICS["class_events"]],
            group_id="notification_consumer",
        )

    async def run(self):
        await self.consumer.start()
        logger.info("notification_worker_started")

        try:
            async for message in self.consumer:
                try:
                    event = message.value
                    event_type = event.get("event_type", "unknown")

                    if event_type == "class.booked":
                        logger.info(
                            "notification_class_booked",
                            class_id=event.get("class_id"),
                            member_id=event.get("member_id"),
                            message=f"Member {event.get('member_id')} booked class {event.get('class_id')}",
                        )

                    elif event_type == "class.cancelled":
                        logger.info(
                            "notification_class_cancelled",
                            class_id=event.get("class_id"),
                            name=event.get("name"),
                            message=f"Class {event.get('name')} has been cancelled. Notify participants.",
                        )

                    elif event_type == "class.unbooked":
                        logger.info(
                            "notification_class_unbooked",
                            class_id=event.get("class_id"),
                            member_id=event.get("member_id"),
                            message=f"Spot opened in class {event.get('class_id')}. Check waitlist.",
                        )

                except Exception as e:
                    logger.error("notification_worker_error", error=str(e))
        finally:
            await self.consumer.stop()
