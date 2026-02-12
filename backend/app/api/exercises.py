from fastapi import APIRouter, HTTPException, Query

from app.models.exercise import (
    ExerciseInfo,
    ExerciseSessionResponse,
    ExerciseSessionListResponse,
    EXERCISE_CATALOG,
)
from app.services.exercise_session_service import ExerciseSessionService

router = APIRouter(prefix="/api/exercises", tags=["Exercises"])


@router.get("", response_model=list[ExerciseInfo])
async def list_exercises():
    """List all supported exercises with their metadata."""
    return EXERCISE_CATALOG


@router.get("/sessions", response_model=ExerciseSessionListResponse)
async def list_sessions(
    member_id: str | None = None,
    exercise: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    """List completed exercise sessions with optional filters."""
    return await ExerciseSessionService.list_sessions(
        member_id=member_id, exercise=exercise, limit=limit
    )


@router.get("/sessions/{session_id}", response_model=ExerciseSessionResponse)
async def get_session(session_id: str):
    """Get a specific exercise session by ID."""
    session = await ExerciseSessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
