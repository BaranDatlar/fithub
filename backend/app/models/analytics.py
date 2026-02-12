from pydantic import BaseModel


class OverviewAnalytics(BaseModel):
    total_members: int = 0
    active_members: int = 0
    new_members_this_month: int = 0
    classes_this_week: int = 0
    avg_class_attendance: float = 0.0
    most_popular_class: str | None = None
    total_workouts_logged: int = 0
    ai_sessions_this_month: int = 0


class MemberAnalytics(BaseModel):
    total: int = 0
    active: int = 0
    frozen: int = 0
    expired: int = 0
    by_plan: dict[str, int] = {}
    new_this_month: int = 0
    growth_rate: float = 0.0


class ClassAnalytics(BaseModel):
    total_classes: int = 0
    avg_attendance_rate: float = 0.0
    by_category: dict[str, int] = {}
    most_popular: str | None = None
    total_bookings: int = 0


class RevenueAnalytics(BaseModel):
    total_members_by_plan: dict[str, int] = {}
    estimated_monthly: float = 0.0
