from datetime import datetime

from bson import ObjectId
import structlog

from app.db.mongodb import get_database
from app.models.gym_class import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassListResponse,
)
from app.services.redis_service import RedisService
from app.services.kafka_service import publish_event, TOPICS
from app.config import settings

logger = structlog.get_logger()

COLLECTION = "classes"


class ClassService:
    @staticmethod
    async def create(data: ClassCreate) -> ClassResponse:
        db = get_database()
        now = datetime.utcnow()

        doc = {
            **data.model_dump(),
            "schedule": data.schedule.model_dump(),
            "current_bookings": 0,
            "participants": [],
            "status": "scheduled",
            "created_at": now,
        }

        result = await db[COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id

        # Initialize Redis capacity counter
        await RedisService.set_capacity(
            str(result.inserted_id),
            data.capacity,
            settings.class_capacity_cache_ttl,
        )

        logger.info("class_created", class_id=str(result.inserted_id))
        return ClassResponse.from_mongo(doc)

    @staticmethod
    async def get_by_id(class_id: str) -> ClassResponse | None:
        db = get_database()
        doc = await db[COLLECTION].find_one({"_id": ObjectId(class_id)})
        if not doc:
            return None
        return ClassResponse.from_mongo(doc)

    @staticmethod
    async def list_classes(
        category: str | None = None,
        day_of_week: int | None = None,
        status: str | None = None,
    ) -> ClassListResponse:
        db = get_database()
        query: dict = {}

        if category:
            query["category"] = category
        if day_of_week is not None:
            query["schedule.day_of_week"] = day_of_week
        if status:
            query["status"] = status

        total = await db[COLLECTION].count_documents(query)
        cursor = db[COLLECTION].find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)

        return ClassListResponse(
            items=[ClassResponse.from_mongo(doc) for doc in docs],
            total=total,
        )

    @staticmethod
    async def update(class_id: str, data: ClassUpdate) -> ClassResponse | None:
        db = get_database()
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await ClassService.get_by_id(class_id)

        set_fields: dict = {}
        for key, value in update_data.items():
            if isinstance(value, dict):
                for nk, nv in value.items():
                    set_fields[f"{key}.{nk}"] = nv
            else:
                set_fields[key] = value

        # If capacity changed, update Redis
        if "capacity" in update_data:
            current = await ClassService.get_by_id(class_id)
            if current:
                new_spots = update_data["capacity"] - current.current_bookings
                await RedisService.set_capacity(
                    class_id, max(0, new_spots), settings.class_capacity_cache_ttl
                )

        result = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(class_id)},
            {"$set": set_fields},
            return_document=True,
        )

        if not result:
            return None

        logger.info("class_updated", class_id=class_id)
        return ClassResponse.from_mongo(result)

    @staticmethod
    async def delete(class_id: str) -> bool:
        db = get_database()
        result = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(class_id)},
            {"$set": {"status": "cancelled"}},
        )
        if not result:
            return False

        await RedisService.invalidate(f"class:{class_id}:spots_left")

        await publish_event(
            TOPICS["class_events"],
            "class.cancelled",
            {"class_id": class_id, "name": result["name"]},
            key=class_id,
        )

        logger.info("class_cancelled", class_id=class_id)
        return True

    @staticmethod
    async def book(class_id: str, member_id: str) -> dict:
        """
        Atomic booking using Redis DECR to prevent race conditions.
        Flow: Redis DECR -> if >= 0 -> MongoDB update -> Kafka event
              if < 0 -> Redis INCR (rollback) -> reject
        """
        db = get_database()

        # Check if capacity counter exists in Redis, init if not
        spots = await RedisService.get_capacity(class_id)
        if spots is None:
            cls = await db[COLLECTION].find_one({"_id": ObjectId(class_id)})
            if not cls:
                raise ValueError("Class not found")
            remaining = cls["capacity"] - cls.get("current_bookings", 0)
            await RedisService.set_capacity(
                class_id, remaining, settings.class_capacity_cache_ttl
            )

        # Check if already booked
        existing = await db[COLLECTION].find_one(
            {"_id": ObjectId(class_id), "participants": ObjectId(member_id)}
        )
        if existing:
            raise ValueError("Member already booked for this class")

        # Atomic decrement
        remaining = await RedisService.decrement_capacity(class_id)

        if remaining < 0:
            # Rollback — no spots left
            await RedisService.increment_capacity(class_id)
            raise ValueError("Class is full")

        # Update MongoDB
        await db[COLLECTION].update_one(
            {"_id": ObjectId(class_id)},
            {
                "$push": {"participants": ObjectId(member_id)},
                "$inc": {"current_bookings": 1},
            },
        )

        # Publish Kafka event
        await publish_event(
            TOPICS["class_events"],
            "class.booked",
            {"class_id": class_id, "member_id": member_id},
            key=class_id,
        )

        logger.info(
            "class_booked", class_id=class_id, member_id=member_id, spots_left=remaining
        )
        return {"message": "Booked successfully", "spots_left": remaining}

    @staticmethod
    async def unbook(class_id: str, member_id: str) -> dict:
        db = get_database()

        result = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(class_id), "participants": ObjectId(member_id)},
            {
                "$pull": {"participants": ObjectId(member_id)},
                "$inc": {"current_bookings": -1},
            },
            return_document=True,
        )

        if not result:
            raise ValueError("Booking not found")

        # Increment Redis capacity
        remaining = await RedisService.increment_capacity(class_id)

        await publish_event(
            TOPICS["class_events"],
            "class.unbooked",
            {"class_id": class_id, "member_id": member_id},
            key=class_id,
        )

        logger.info("class_unbooked", class_id=class_id, member_id=member_id)
        return {"message": "Booking cancelled", "spots_left": remaining}

    @staticmethod
    async def get_participants(class_id: str) -> list[dict]:
        db = get_database()
        cls = await db[COLLECTION].find_one({"_id": ObjectId(class_id)})
        if not cls:
            return []

        if not cls.get("participants"):
            return []

        members = (
            await db["members"]
            .find({"_id": {"$in": cls["participants"]}, "is_deleted": {"$ne": True}})
            .to_list(length=100)
        )

        return [
            {
                "id": str(m["_id"]),
                "first_name": m["first_name"],
                "last_name": m["last_name"],
                "email": m["email"],
            }
            for m in members
        ]
