from fastapi import APIRouter, HTTPException, Query

from app.models.workout import (
    WorkoutPlanCreate,
    WorkoutPlanUpdate,
    WorkoutPlanResponse,
    WorkoutPlanListResponse,
    WorkoutAssign,
    WorkoutLogCreate,
    WorkoutLogResponse,
)
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/api/workouts", tags=["Workouts"])


# --- Plans ---

@router.post("/plans", response_model=WorkoutPlanResponse, status_code=201)
async def create_plan(data: WorkoutPlanCreate):
    return await WorkoutService.create_plan(data)


@router.get("/plans", response_model=WorkoutPlanListResponse)
async def list_plans(difficulty: str | None = None):
    return await WorkoutService.list_plans(difficulty=difficulty)


@router.get("/plans/{plan_id}", response_model=WorkoutPlanResponse)
async def get_plan(plan_id: str):
    plan = await WorkoutService.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return plan


@router.put("/plans/{plan_id}", response_model=WorkoutPlanResponse)
async def update_plan(plan_id: str, data: WorkoutPlanUpdate):
    plan = await WorkoutService.update_plan(plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return plan


# --- Assignment ---

@router.post("/assign")
async def assign_plan(data: WorkoutAssign):
    try:
        return await WorkoutService.assign_plan(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/member/{member_id}", response_model=list[WorkoutPlanResponse])
async def get_member_workouts(member_id: str):
    return await WorkoutService.get_member_workouts(member_id)


# --- Logging ---

@router.post("/log", response_model=WorkoutLogResponse, status_code=201)
async def log_workout(data: WorkoutLogCreate):
    return await WorkoutService.log_workout(data)


@router.get("/member/{member_id}/logs", response_model=list[WorkoutLogResponse])
async def get_member_logs(
    member_id: str,
    limit: int = Query(20, ge=1, le=100),
):
    return await WorkoutService.get_member_logs(member_id, limit=limit)
