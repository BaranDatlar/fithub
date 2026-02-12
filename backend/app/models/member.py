from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class MembershipPlan(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    PT = "pt"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    EXPIRED = "expired"


class FitnessLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Membership(BaseModel):
    plan: MembershipPlan = MembershipPlan.BASIC
    status: MembershipStatus = MembershipStatus.ACTIVE
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime | None = None


class Profile(BaseModel):
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    fitness_level: FitnessLevel = FitnessLevel.BEGINNER
    goals: list[str] = Field(default_factory=list)


# --- Request Schemas ---

class MemberCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    membership: Membership = Field(default_factory=Membership)
    profile: Profile = Field(default_factory=Profile)


class MemberUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    membership: Membership | None = None
    profile: Profile | None = None


# --- Response Schemas ---

class MemberResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    membership: Membership
    profile: Profile
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, doc: dict) -> "MemberResponse":
        return cls(
            id=str(doc["_id"]),
            first_name=doc["first_name"],
            last_name=doc["last_name"],
            email=doc["email"],
            phone=doc.get("phone"),
            membership=Membership(**doc["membership"]),
            profile=Profile(**doc["profile"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )


class MemberListResponse(BaseModel):
    items: list[MemberResponse]
    total: int
    page: int
    page_size: int


class MemberStats(BaseModel):
    total_workouts: int = 0
    total_classes_attended: int = 0
    avg_form_score: float | None = None
    last_activity: datetime | None = None
