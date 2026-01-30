from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.deps.organizer import (
    get_organizer_by_id,
    require_organizer_admin,
    get_user_organizer_membership
)
from app.models.user import User
from app.models.organizer import Organizer
from app.models.organizer_member import OrganizerMember
from app.schemas.organizer_member import (
    OrganizerMemberInvite,
    OrganizerMemberUpdate,
    OrganizerMemberResponse,
    OrganizerMemberWithUserResponse
)
from app.services.organizer_member_service import OrganizerMemberService
from app.schemas.organizer_member import OrganizerMemberInviteByEmail


router = APIRouter()


@router.post(
    "/{organizer_id}/members",
    response_model=OrganizerMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite member ke organizer"
)
async def invite_member(
    organizer_id: int,
    invite_data: OrganizerMemberInvite,
    _: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Invite user menjadi member organizer.
    Hanya ORGANIZER_ADMIN yang bisa.
    """
    member = await OrganizerMemberService.invite_member(
        db, organizer_id, invite_data
    )
    return member


@router.get(
    "/{organizer_id}/members",
    response_model=List[OrganizerMemberWithUserResponse],
    summary="Get daftar member organizer"
)
async def get_organizer_members(
    organizer_id: int,
    _: Annotated[OrganizerMember, Depends(get_user_organizer_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """
    Get semua member dari organizer.
    Semua member aktif bisa lihat daftar member.
    """
    members = await OrganizerMemberService.get_organizer_members(
        db, organizer_id, skip, limit
    )
    
    # Load user data untuk setiap member
    result = []
    for member in members:
        user = await db.get(User, member.user_id)
        member_dict = OrganizerMemberResponse.model_validate(member).model_dump()
        member_dict['user_name'] = user.full_name if user else None
        member_dict['user_email'] = user.email if user else None
        result.append(member_dict)
    
    return result


@router.get(
    "/{organizer_id}/members/{user_id}",
    response_model=OrganizerMemberWithUserResponse,
    summary="Get detail member"
)
async def get_member_detail(
    organizer_id: int,
    user_id: int,
    _: Annotated[OrganizerMember, Depends(get_user_organizer_membership)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get detail member tertentu"""
    member = await OrganizerMemberService.get_member(db, organizer_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member tidak ditemukan"
        )
    
    user = await db.get(User, user_id)
    member_dict = OrganizerMemberResponse.model_validate(member).model_dump()
    member_dict['user_name'] = user.full_name if user else None
    member_dict['user_email'] = user.email if user else None
    
    return member_dict


@router.patch(
    "/{organizer_id}/members/{user_id}",
    response_model=OrganizerMemberResponse,
    summary="Update role/status member"
)
async def update_member(
    organizer_id: int,
    user_id: int,
    update_data: OrganizerMemberUpdate,
    current_member: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update role atau status member.
    Hanya ORGANIZER_ADMIN yang bisa.
    Tidak bisa update diri sendiri.
    """
    # Cek tidak update diri sendiri
    if user_id == current_member.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak dapat mengubah role/status diri sendiri"
        )
    
    member = await OrganizerMemberService.get_member(db, organizer_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member tidak ditemukan"
        )
    
    updated_member = await OrganizerMemberService.update_member(
        db, member, update_data
    )
    return updated_member


@router.delete(
    "/{organizer_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member dari organizer"
)
async def remove_member(
    organizer_id: int,
    user_id: int,
    current_member: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Remove member dari organizer.
    Hanya ORGANIZER_ADMIN yang bisa.
    Tidak bisa remove diri sendiri.
    """
    # Cek tidak remove diri sendiri
    if user_id == current_member.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak dapat menghapus diri sendiri dari organizer"
        )
    
    member = await OrganizerMemberService.get_member(db, organizer_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member tidak ditemukan"
        )
    
    await OrganizerMemberService.remove_member(db, member)
    return None


@router.post(
    "/{organizer_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Leave organizer (keluar sendiri)"
)
async def leave_organizer(
    organizer_id: int,
    current_member: Annotated[OrganizerMember, Depends(get_user_organizer_membership)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    User keluar dari organizer.
    
    Aturan:
    - ORGANIZER_ADMIN tidak bisa leave jika dia satu-satunya admin
    """
    from sqlalchemy import select, func
    from app.models.organizer_member import Role, Status as MemberStatus
    
    # Jika user adalah admin, cek apakah ada admin lain
    if current_member.role == Role.ORGANIZER_ADMIN:
        admin_count_query = select(func.count()).select_from(OrganizerMember).where(
            OrganizerMember.organizer_id == organizer_id,
            OrganizerMember.role == Role.ORGANIZER_ADMIN,
            OrganizerMember.status == MemberStatus.ACTIVE
        )
        result = await db.execute(admin_count_query)
        admin_count = result.scalar()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak dapat keluar. Anda adalah satu-satunya admin. Transfer role admin ke user lain terlebih dahulu."
            )
    
    await OrganizerMemberService.remove_member(db, current_member)
    return None

@router.post(
    "/{organizer_id}/members/invite-by-email",
    response_model=OrganizerMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite member by email"
)
async def invite_member_by_email(
    organizer_id: int,
    invite_data: OrganizerMemberInviteByEmail,
    _: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Invite user by email.
    User harus sudah register terlebih dahulu.
    """
    member = await OrganizerMemberService.invite_by_email(
        db, organizer_id, invite_data
    )
    return member