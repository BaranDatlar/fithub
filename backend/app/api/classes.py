from fastapi import APIRouter, HTTPException, Query

from app.models.gym_class import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassListResponse,
)
from app.services.class_service import ClassService

router = APIRouter(prefix="/api/classes", tags=["Classes"])


@router.post("", response_model=ClassResponse, status_code=201)
async def create_class(data: ClassCreate):
    return await ClassService.create(data)


@router.get("", response_model=ClassListResponse)
async def list_classes(
    category: str | None = None,
    day_of_week: int | None = Query(None, ge=0, le=6),
    status: str | None = None,
):
    return await ClassService.list_classes(
        category=category, day_of_week=day_of_week, status=status
    )


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(class_id: str):
    cls = await ClassService.get_by_id(class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(class_id: str, data: ClassUpdate):
    cls = await ClassService.update(class_id, data)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls


@router.delete("/{class_id}", status_code=204)
async def delete_class(class_id: str):
    deleted = await ClassService.delete(class_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Class not found")


@router.post("/{class_id}/book")
async def book_class(class_id: str, member_id: str = Query(...)):
    try:
        return await ClassService.book(class_id, member_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{class_id}/book")
async def unbook_class(class_id: str, member_id: str = Query(...)):
    try:
        return await ClassService.unbook(class_id, member_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{class_id}/participants")
async def get_participants(class_id: str):
    cls = await ClassService.get_by_id(class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return await ClassService.get_participants(class_id)
