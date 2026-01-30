from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.models.organizer import Organizer
from app.models.organizer_member import OrganizerMember, Role, Status as MemberStatus
from app.services.organizer_service import OrganizerService


async def get_organizer_by_id(
    organizer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Organizer:
    """Dependency untuk get organizer by ID"""
    return await OrganizerService.get_organizer_by_id(db, organizer_id)


async def get_user_organizer_membership(
    organizer: Annotated[Organizer, Depends(get_organizer_by_id)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> OrganizerMember:
    """Cek apakah user adalah member dari organizer"""
    from app.services.organizer_member_service import OrganizerMemberService
    
    member = await OrganizerMemberService.get_member(
        db, organizer.id, current_user.id
    )
    
    if not member or member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda bukan member dari organizer ini"
        )
    
    return member


async def require_organizer_admin(
    member: Annotated[OrganizerMember, Depends(get_user_organizer_membership)]
) -> OrganizerMember:
    """Require user harus ORGANIZER_ADMIN"""
    if member.role != Role.ORGANIZER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin organizer yang dapat melakukan aksi ini"
        )
    return member


async def require_organizer_admin_or_finance(
    member: Annotated[OrganizerMember, Depends(get_user_organizer_membership)]
) -> OrganizerMember:
    """Require user harus ORGANIZER_ADMIN atau FINANCE"""
    if member.role not in [Role.ORGANIZER_ADMIN, Role.FINANCE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin atau finance yang dapat melakukan aksi ini"
        )
    return member
    