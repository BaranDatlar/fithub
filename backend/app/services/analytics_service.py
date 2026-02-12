from datetime import datetime, timedelta

import structlog

from app.db.mongodb import get_database
from app.models.analytics import (
    OverviewAnalytics,
    MemberAnalytics,
    ClassAnalytics,
    RevenueAnalytics,
)
from app.services.redis_service import RedisService
from app.config import settings

logger = structlog.get_logger()

PLAN_PRICES = {"basic": 29.99, "premium": 49.99, "pt": 89.99}


class AnalyticsService:
    @staticmethod
    async def get_overview() -> OverviewAnalytics:
        cache_key = "analytics:overview"
        cached = await RedisService.get_cached(cache_key)
        if cached:
            return OverviewAnalytics(**cached)

        db = get_database()
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=now.weekday())

        total_members = await db["members"].count_documents(
            {"is_deleted": {"$ne": True}}
        )
        active_members = await db["members"].count_documents(
            {"is_deleted": {"$ne": True}, "membership.status": "active"}
        )
        new_this_month = await db["members"].count_documents(
            {"is_deleted": {"$ne": True}, "created_at": {"$gte": month_start}}
        )

        classes_this_week = await db["classes"].count_documents(
            {"status": "scheduled", "created_at": {"$gte": week_start}}
        )

        # Average class attendance
        pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}, "capacity": {"$gt": 0}}},
            {
                "$project": {
                    "attendance_rate": {"$divide": ["$current_bookings", "$capacity"]}
                }
            },
            {"$group": {"_id": None, "avg": {"$avg": "$attendance_rate"}}},
        ]
        att_result = await db["classes"].aggregate(pipeline).to_list(1)
        avg_attendance = round(att_result[0]["avg"], 2) if att_result else 0.0

        # Most popular class
        pop_pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {"$sort": {"current_bookings": -1}},
            {"$limit": 1},
        ]
        pop_result = await db["classes"].aggregate(pop_pipeline).to_list(1)
        most_popular = pop_result[0]["name"] if pop_result else None

        total_workouts = await db["workout_logs"].count_documents({})

        ai_sessions = await db["workout_logs"].count_documents(
            {"source": "ai_tracker", "completed_at": {"$gte": month_start}}
        )

        result = OverviewAnalytics(
            total_members=total_members,
            active_members=active_members,
            new_members_this_month=new_this_month,
            classes_this_week=classes_this_week,
            avg_class_attendance=avg_attendance,
            most_popular_class=most_popular,
            total_workouts_logged=total_workouts,
            ai_sessions_this_month=ai_sessions,
        )

        await RedisService.set_cached(
            cache_key, result.model_dump(), settings.dashboard_cache_ttl
        )
        return result

    @staticmethod
    async def get_member_analytics() -> MemberAnalytics:
        cache_key = "analytics:members"
        cached = await RedisService.get_cached(cache_key)
        if cached:
            return MemberAnalytics(**cached)

        db = get_database()
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_month_start = (month_start - timedelta(days=1)).replace(day=1)

        base_filter = {"is_deleted": {"$ne": True}}

        total = await db["members"].count_documents(base_filter)
        active = await db["members"].count_documents(
            {**base_filter, "membership.status": "active"}
        )
        frozen = await db["members"].count_documents(
            {**base_filter, "membership.status": "frozen"}
        )
        expired = await db["members"].count_documents(
            {**base_filter, "membership.status": "expired"}
        )

        # By plan
        plan_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$membership.plan", "count": {"$sum": 1}}},
        ]
        plan_result = await db["members"].aggregate(plan_pipeline).to_list(10)
        by_plan = {r["_id"]: r["count"] for r in plan_result}

        new_this_month = await db["members"].count_documents(
            {**base_filter, "created_at": {"$gte": month_start}}
        )
        new_prev_month = await db["members"].count_documents(
            {
                **base_filter,
                "created_at": {"$gte": prev_month_start, "$lt": month_start},
            }
        )
        growth_rate = round(
            (new_this_month - new_prev_month) / max(new_prev_month, 1) * 100, 1
        )

        result = MemberAnalytics(
            total=total,
            active=active,
            frozen=frozen,
            expired=expired,
            by_plan=by_plan,
            new_this_month=new_this_month,
            growth_rate=growth_rate,
        )

        await RedisService.set_cached(
            cache_key, result.model_dump(), settings.dashboard_cache_ttl
        )
        return result

    @staticmethod
    async def get_class_analytics() -> ClassAnalytics:
        cache_key = "analytics:classes"
        cached = await RedisService.get_cached(cache_key)
        if cached:
            return ClassAnalytics(**cached)

        db = get_database()

        total_classes = await db["classes"].count_documents({})

        # Attendance rate
        pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}, "capacity": {"$gt": 0}}},
            {"$project": {"rate": {"$divide": ["$current_bookings", "$capacity"]}}},
            {"$group": {"_id": None, "avg": {"$avg": "$rate"}}},
        ]
        att_result = await db["classes"].aggregate(pipeline).to_list(1)
        avg_rate = round(att_result[0]["avg"], 2) if att_result else 0.0

        # By category
        cat_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        ]
        cat_result = await db["classes"].aggregate(cat_pipeline).to_list(10)
        by_category = {r["_id"]: r["count"] for r in cat_result}

        # Most popular
        pop_pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {"$sort": {"current_bookings": -1}},
            {"$limit": 1},
        ]
        pop_result = await db["classes"].aggregate(pop_pipeline).to_list(1)
        most_popular = pop_result[0]["name"] if pop_result else None

        # Total bookings
        booking_pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$current_bookings"}}},
        ]
        booking_result = await db["classes"].aggregate(booking_pipeline).to_list(1)
        total_bookings = booking_result[0]["total"] if booking_result else 0

        result = ClassAnalytics(
            total_classes=total_classes,
            avg_attendance_rate=avg_rate,
            by_category=by_category,
            most_popular=most_popular,
            total_bookings=total_bookings,
        )

        await RedisService.set_cached(
            cache_key, result.model_dump(), settings.dashboard_cache_ttl
        )
        return result

    @staticmethod
    async def get_revenue_analytics() -> RevenueAnalytics:
        cache_key = "analytics:revenue"
        cached = await RedisService.get_cached(cache_key)
        if cached:
            return RevenueAnalytics(**cached)

        db = get_database()

        plan_pipeline = [
            {"$match": {"is_deleted": {"$ne": True}, "membership.status": "active"}},
            {"$group": {"_id": "$membership.plan", "count": {"$sum": 1}}},
        ]
        plan_result = await db["members"].aggregate(plan_pipeline).to_list(10)
        by_plan = {r["_id"]: r["count"] for r in plan_result}

        estimated_monthly = sum(
            count * PLAN_PRICES.get(plan, 0) for plan, count in by_plan.items()
        )

        result = RevenueAnalytics(
            total_members_by_plan=by_plan,
            estimated_monthly=round(estimated_monthly, 2),
        )

        await RedisService.set_cached(
            cache_key, result.model_dump(), settings.dashboard_cache_ttl
        )
        return result
