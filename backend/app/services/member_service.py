from datetime import datetime

from bson import ObjectId
import structlog

from app.db.mongodb import get_database
from app.models.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MemberStats,
)
from app.services.redis_service import RedisService
from app.services.kafka_service import publish_event, TOPICS

logger = structlog.get_logger()

COLLECTION = "members"


class MemberService:
    @staticmethod
    async def create(data: MemberCreate) -> MemberResponse:
        db = get_database()

        # Check for duplicate email
        existing = await db[COLLECTION].find_one(
            {"email": data.email, "is_deleted": {"$ne": True}}
        )
        if existing:
            raise ValueError(f"Member with email {data.email} already exists")

        now = datetime.utcnow()
        doc = {
            **data.model_dump(),
            "membership": data.membership.model_dump(),
            "profile": data.profile.model_dump(),
            "created_at": now,
            "updated_at": now,
            "is_deleted": False,
        }

        result = await db[COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id

        # Invalidate member count cache
        await RedisService.invalidate("analytics:member_count")

        # Publish Kafka event
        await publish_event(
            TOPICS["member_events"],
            "member.created",
            {
                "member_id": str(result.inserted_id),
                "email": data.email,
                "plan": data.membership.plan.value,
            },
            key=str(result.inserted_id),
        )

        logger.info("member_created", member_id=str(result.inserted_id))
        return MemberResponse.from_mongo(doc)

    @staticmethod
    async def get_by_id(member_id: str) -> MemberResponse | None:
        db = get_database()
        doc = await db[COLLECTION].find_one(
            {"_id": ObjectId(member_id), "is_deleted": {"$ne": True}}
        )
        if not doc:
            return None
        return MemberResponse.from_mongo(doc)

    @staticmethod
    async def list_members(
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        plan: str | None = None,
    ) -> MemberListResponse:
        db = get_database()
        query: dict = {"is_deleted": {"$ne": True}}

        if search:
            query["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]

        if status:
            query["membership.status"] = status

        if plan:
            query["membership.plan"] = plan

        total = await db[COLLECTION].count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            db[COLLECTION]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=page_size)

        return MemberListResponse(
            items=[MemberResponse.from_mongo(doc) for doc in docs],
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def update(member_id: str, data: MemberUpdate) -> MemberResponse | None:
        db = get_database()

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await MemberService.get_by_id(member_id)

        # Flatten nested models for MongoDB update
        set_fields = {"updated_at": datetime.utcnow()}
        for key, value in update_data.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    set_fields[f"{key}.{nested_key}"] = nested_value
            else:
                set_fields[key] = value

        result = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(member_id), "is_deleted": {"$ne": True}},
            {"$set": set_fields},
            return_document=True,
        )

        if not result:
            return None

        # Publish Kafka event
        await publish_event(
            TOPICS["member_events"],
            "member.updated",
            {"member_id": member_id, "updated_fields": list(update_data.keys())},
            key=member_id,
        )

        logger.info("member_updated", member_id=member_id)
        return MemberResponse.from_mongo(result)

    @staticmethod
    async def delete(member_id: str) -> bool:
        db = get_database()
        result = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(member_id), "is_deleted": {"$ne": True}},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}},
        )

        if not result:
            return False

        await RedisService.invalidate("analytics:member_count")

        await publish_event(
            TOPICS["member_events"],
            "member.deleted",
            {"member_id": member_id},
            key=member_id,
        )

        logger.info("member_deleted", member_id=member_id)
        return True

    @staticmethod
    async def get_stats(member_id: str) -> MemberStats:
        db = get_database()

        # Count workout logs
        total_workouts = await db["workout_logs"].count_documents(
            {"member_id": ObjectId(member_id)}
        )

        # Count class participations
        total_classes = await db["classes"].count_documents(
            {"participants": ObjectId(member_id)}
        )

        # Get average form score from workout logs
        pipeline = [
            {"$match": {"member_id": ObjectId(member_id)}},
            {"$unwind": "$exercises_completed"},
            {"$match": {"exercises_completed.form_score": {"$ne": None}}},
            {
                "$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$exercises_completed.form_score"},
                }
            },
        ]
        avg_result = await db["workout_logs"].aggregate(pipeline).to_list(1)
        avg_form_score = avg_result[0]["avg_score"] if avg_result else None

        # Last activity
        last_log = await db["workout_logs"].find_one(
            {"member_id": ObjectId(member_id)},
            sort=[("completed_at", -1)],
        )

        return MemberStats(
            total_workouts=total_workouts,
            total_classes_attended=total_classes,
            avg_form_score=round(avg_form_score, 1) if avg_form_score else None,
            last_activity=last_log["completed_at"] if last_log else None,
        )
