from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ClassCategory(str, Enum):
    YOGA = "yoga"
    HIIT = "hiit"
    STRENGTH = "strength"
    CARDIO = "cardio"
    PILATES = "pilates"


class ClassStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Schedule(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    recurring: bool = False


# --- Request Schemas ---


class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    instructor: str = Field(..., min_length=1)
    category: ClassCategory
    schedule: Schedule
    capacity: int = Field(..., gt=0, le=100)
    location: str = Field(default="Main Floor")


class ClassUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    instructor: str | None = None
    category: ClassCategory | None = None
    schedule: Schedule | None = None
    capacity: int | None = None
    location: str | None = None
    status: ClassStatus | None = None


# --- Response Schemas ---


class ClassResponse(BaseModel):
    id: str
    name: str
    description: str
    instructor: str
    category: ClassCategory
    schedule: Schedule
    capacity: int
    current_bookings: int
    participants: list[str]
    location: str
    status: ClassStatus
    created_at: datetime

    @classmethod
    def from_mongo(cls, doc: dict) -> "ClassResponse":
        return cls(
            id=str(doc["_id"]),
            name=doc["name"],
            description=doc.get("description", ""),
            instructor=doc["instructor"],
            category=doc["category"],
            schedule=Schedule(**doc["schedule"]),
            capacity=doc["capacity"],
            current_bookings=doc.get("current_bookings", 0),
            participants=[str(p) for p in doc.get("participants", [])],
            location=doc.get("location", "Main Floor"),
            status=doc.get("status", "scheduled"),
            created_at=doc["created_at"],
        )


class ClassListResponse(BaseModel):
    items: list[ClassResponse]
    total: int
