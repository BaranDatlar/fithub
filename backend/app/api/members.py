from fastapi import APIRouter, HTTPException, Query

from app.models.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MemberStats,
)
from app.services.member_service import MemberService

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.post("", response_model=MemberResponse, status_code=201)
async def create_member(data: MemberCreate):
    try:
        return await MemberService.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=MemberListResponse)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    plan: str | None = None,
):
    return await MemberService.list_members(
        page=page, page_size=page_size, search=search, status=status, plan=plan
    )


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(member_id: str):
    member = await MemberService.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(member_id: str, data: MemberUpdate):
    member = await MemberService.update(member_id, data)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete("/{member_id}", status_code=204)
async def delete_member(member_id: str):
    deleted = await MemberService.delete(member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")


@router.get("/{member_id}/stats", response_model=MemberStats)
async def get_member_stats(member_id: str):
    member = await MemberService.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return await MemberService.get_stats(member_id)
