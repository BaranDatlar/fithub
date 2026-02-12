from fastapi import APIRouter

from app.models.analytics import (
    OverviewAnalytics,
    MemberAnalytics,
    ClassAnalytics,
    RevenueAnalytics,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalytics)
async def get_overview():
    return await AnalyticsService.get_overview()


@router.get("/members", response_model=MemberAnalytics)
async def get_member_analytics():
    return await AnalyticsService.get_member_analytics()


@router.get("/classes", response_model=ClassAnalytics)
async def get_class_analytics():
    return await AnalyticsService.get_class_analytics()


@router.get("/revenue", response_model=RevenueAnalytics)
async def get_revenue_analytics():
    return await AnalyticsService.get_revenue_analytics()
