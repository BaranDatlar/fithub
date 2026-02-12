import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import structlog

from app.config import settings

logger = structlog.get_logger()

_producer: AIOKafkaProducer | None = None

# Topic definitions
TOPICS = {
    "member_events": "member.events",
    "class_events": "class.events",
    "workout_events": "workout.events",
    "exercise_events": "exercise.events",
}


async def start_producer() -> None:
    global _producer
    _producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )
    await _producer.start()
    logger.info("kafka_producer_started")


async def stop_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("kafka_producer_stopped")


async def publish_event(
    topic: str, event_type: str, data: dict, key: str | None = None
) -> None:
    if _producer is None:
        logger.warning(
            "kafka_producer_not_available", topic=topic, event_type=event_type
        )
        return
    event = {"event_type": event_type, **data}
    await _producer.send(topic, value=event, key=key)
    logger.info("kafka_event_published", topic=topic, event_type=event_type)


def create_consumer(topics: list[str], group_id: str) -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
