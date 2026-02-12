from datetime import datetime

from bson import ObjectId
import structlog

from app.db.mongodb import get_database
from app.models.workout import (
    WorkoutPlanCreate,
    WorkoutPlanUpdate,
    WorkoutPlanResponse,
    WorkoutPlanListResponse,
    WorkoutAssign,
    WorkoutLogCreate,
    WorkoutLogResponse,
)
from app.services.kafka_service import publish_event, TOPICS

logger = structlog.get_logger()

PLANS_COLLECTION = "workout_plans"
LOGS_COLLECTION = "workout_logs"
ASSIGNMENTS_COLLECTION = "workout_assignments"


class WorkoutService:
    # --- Plans ---

    @staticmethod
    async def create_plan(data: WorkoutPlanCreate) -> WorkoutPlanResponse:
        db = get_database()
        now = datetime.utcnow()

        doc = {
            **data.model_dump(),
            "exercises": [e.model_dump() for e in data.exercises],
            "created_at": now,
        }

        result = await db[PLANS_COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id

        logger.info("workout_plan_created", plan_id=str(result.inserted_id))
        return WorkoutPlanResponse.from_mongo(doc)

    @staticmethod
    async def get_plan(plan_id: str) -> WorkoutPlanResponse | None:
        db = get_database()
        doc = await db[PLANS_COLLECTION].find_one({"_id": ObjectId(plan_id)})
        if not doc:
            return None
        return WorkoutPlanResponse.from_mongo(doc)

    @staticmethod
    async def list_plans(
        difficulty: str | None = None,
    ) -> WorkoutPlanListResponse:
        db = get_database()
        query: dict = {}
        if difficulty:
            query["difficulty"] = difficulty

        total = await db[PLANS_COLLECTION].count_documents(query)
        cursor = db[PLANS_COLLECTION].find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)

        return WorkoutPlanListResponse(
            items=[WorkoutPlanResponse.from_mongo(doc) for doc in docs],
            total=total,
        )

    @staticmethod
    async def update_plan(
        plan_id: str, data: WorkoutPlanUpdate
    ) -> WorkoutPlanResponse | None:
        db = get_database()
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await WorkoutService.get_plan(plan_id)

        if "exercises" in update_data:
            update_data["exercises"] = [
                e.model_dump() if hasattr(e, "model_dump") else e
                for e in update_data["exercises"]
            ]

        result = await db[PLANS_COLLECTION].find_one_and_update(
            {"_id": ObjectId(plan_id)},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            return None
        return WorkoutPlanResponse.from_mongo(result)

    # --- Assignment ---

    @staticmethod
    async def assign_plan(data: WorkoutAssign) -> dict:
        db = get_database()

        # Verify member exists
        member = await db["members"].find_one(
            {"_id": ObjectId(data.member_id), "is_deleted": {"$ne": True}}
        )
        if not member:
            raise ValueError("Member not found")

        # Verify plan exists
        plan = await db[PLANS_COLLECTION].find_one({"_id": ObjectId(data.plan_id)})
        if not plan:
            raise ValueError("Workout plan not found")

        assignment = {
            "member_id": ObjectId(data.member_id),
            "plan_id": ObjectId(data.plan_id),
            "assigned_at": datetime.utcnow(),
            "status": "active",
        }
        await db[ASSIGNMENTS_COLLECTION].insert_one(assignment)

        await publish_event(
            TOPICS["workout_events"],
            "workout.plan_assigned",
            {
                "member_id": data.member_id,
                "plan_id": data.plan_id,
                "plan_name": plan["name"],
            },
            key=data.member_id,
        )

        logger.info(
            "workout_plan_assigned", member_id=data.member_id, plan_id=data.plan_id
        )
        return {"message": "Plan assigned successfully", "plan_name": plan["name"]}

    @staticmethod
    async def get_member_workouts(member_id: str) -> list[WorkoutPlanResponse]:
        db = get_database()

        assignments = (
            await db[ASSIGNMENTS_COLLECTION]
            .find({"member_id": ObjectId(member_id), "status": "active"})
            .to_list(length=50)
        )

        plan_ids = [a["plan_id"] for a in assignments]
        if not plan_ids:
            return []

        plans = (
            await db[PLANS_COLLECTION]
            .find({"_id": {"$in": plan_ids}})
            .to_list(length=50)
        )

        return [WorkoutPlanResponse.from_mongo(p) for p in plans]

    # --- Logging ---

    @staticmethod
    async def log_workout(data: WorkoutLogCreate) -> WorkoutLogResponse:
        db = get_database()

        doc = {
            "member_id": ObjectId(data.member_id),
            "plan_id": ObjectId(data.plan_id) if data.plan_id else None,
            "completed_at": datetime.utcnow(),
            "duration_minutes": data.duration_minutes,
            "exercises_completed": [e.model_dump() for e in data.exercises_completed],
            "source": data.source.value,
        }

        result = await db[LOGS_COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id

        await publish_event(
            TOPICS["workout_events"],
            "workout.logged",
            {
                "member_id": data.member_id,
                "plan_id": data.plan_id,
                "duration_minutes": data.duration_minutes,
                "source": data.source.value,
            },
            key=data.member_id,
        )

        logger.info("workout_logged", member_id=data.member_id)
        return WorkoutLogResponse.from_mongo(doc)

    @staticmethod
    async def get_member_logs(
        member_id: str, limit: int = 20
    ) -> list[WorkoutLogResponse]:
        db = get_database()
        cursor = (
            db[LOGS_COLLECTION]
            .find({"member_id": ObjectId(member_id)})
            .sort("completed_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [WorkoutLogResponse.from_mongo(doc) for doc in docs]
