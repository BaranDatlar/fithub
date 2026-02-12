from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ExerciseType(str, Enum):
    SQUAT = "squat"
    BICEP_CURL = "bicep_curl"
    SHOULDER_PRESS = "shoulder_press"


class RepResult(BaseModel):
    rep_number: int
    score: float
    feedback: list[str] = Field(default_factory=list)


class ExerciseSessionCreate(BaseModel):
    member_id: str
    exercise: ExerciseType


class ExerciseSessionResponse(BaseModel):
    id: str
    member_id: str
    exercise: str
    total_reps: int
    avg_form_score: float | None
    rep_details: list[RepResult]
    duration_seconds: int
    started_at: datetime
    ended_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "ExerciseSessionResponse":
        return cls(
            id=str(doc["_id"]),
            member_id=doc["member_id"],
            exercise=doc["exercise"],
            total_reps=doc["total_reps"],
            avg_form_score=doc.get("avg_form_score"),
            rep_details=[RepResult(**r) for r in doc.get("rep_details", [])],
            duration_seconds=doc.get("duration_seconds", 0),
            started_at=doc["started_at"],
            ended_at=doc.get("ended_at"),
        )


class ExerciseSessionListResponse(BaseModel):
    items: list[ExerciseSessionResponse]
    total: int


class ExerciseInfo(BaseModel):
    name: str
    display_name: str
    description: str
    target_muscles: list[str]
    tracked_angle: str


# Static exercise definitions
EXERCISE_CATALOG: list[ExerciseInfo] = [
    ExerciseInfo(
        name="squat",
        display_name="Squat",
        description="Track knee angle for proper squat depth and form",
        target_muscles=["quadriceps", "glutes", "hamstrings"],
        tracked_angle="knee",
    ),
    ExerciseInfo(
        name="bicep_curl",
        display_name="Bicep Curl",
        description="Track elbow angle for full range of motion curls",
        target_muscles=["biceps", "forearms"],
        tracked_angle="elbow",
    ),
    ExerciseInfo(
        name="shoulder_press",
        display_name="Shoulder Press",
        description="Track shoulder angle for overhead press lockout",
        target_muscles=["deltoids", "triceps", "trapezius"],
        tracked_angle="shoulder",
    ),
]
