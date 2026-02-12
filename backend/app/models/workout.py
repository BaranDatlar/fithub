from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WorkoutSource(str, Enum):
    MANUAL = "manual"
    AI_TRACKER = "ai_tracker"


class ExerciseInPlan(BaseModel):
    exercise_id: str | None = None
    name: str
    sets: int = Field(..., gt=0)
    reps: int = Field(..., gt=0)
    rest_seconds: int = Field(default=60, ge=0)
    notes: str = ""


class ExerciseLog(BaseModel):
    exercise_name: str
    sets_completed: int
    reps_per_set: list[int] = Field(default_factory=list)
    form_score: float | None = None


# --- Request Schemas ---


class WorkoutPlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    difficulty: Difficulty = Difficulty.BEGINNER
    exercises: list[ExerciseInPlan] = Field(..., min_length=1)
    estimated_duration_minutes: int = Field(..., gt=0)
    created_by: str = Field(..., min_length=1)


class WorkoutPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty: Difficulty | None = None
    exercises: list[ExerciseInPlan] | None = None
    estimated_duration_minutes: int | None = None


class WorkoutAssign(BaseModel):
    member_id: str
    plan_id: str


class WorkoutLogCreate(BaseModel):
    member_id: str
    plan_id: str | None = None
    duration_minutes: int = Field(..., gt=0)
    exercises_completed: list[ExerciseLog] = Field(default_factory=list)
    source: WorkoutSource = WorkoutSource.MANUAL


# --- Response Schemas ---


class WorkoutPlanResponse(BaseModel):
    id: str
    name: str
    description: str
    difficulty: Difficulty
    exercises: list[ExerciseInPlan]
    estimated_duration_minutes: int
    created_by: str
    created_at: datetime

    @classmethod
    def from_mongo(cls, doc: dict) -> "WorkoutPlanResponse":
        return cls(
            id=str(doc["_id"]),
            name=doc["name"],
            description=doc.get("description", ""),
            difficulty=doc["difficulty"],
            exercises=[ExerciseInPlan(**e) for e in doc["exercises"]],
            estimated_duration_minutes=doc["estimated_duration_minutes"],
            created_by=doc["created_by"],
            created_at=doc["created_at"],
        )


class WorkoutLogResponse(BaseModel):
    id: str
    member_id: str
    plan_id: str | None
    completed_at: datetime
    duration_minutes: int
    exercises_completed: list[ExerciseLog]
    source: WorkoutSource

    @classmethod
    def from_mongo(cls, doc: dict) -> "WorkoutLogResponse":
        return cls(
            id=str(doc["_id"]),
            member_id=str(doc["member_id"]),
            plan_id=str(doc["plan_id"]) if doc.get("plan_id") else None,
            completed_at=doc["completed_at"],
            duration_minutes=doc["duration_minutes"],
            exercises_completed=[
                ExerciseLog(**e) for e in doc.get("exercises_completed", [])
            ],
            source=doc.get("source", "manual"),
        )


class WorkoutPlanListResponse(BaseModel):
    items: list[WorkoutPlanResponse]
    total: int
