from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.deps.organizer import (
    get_organizer_by_id,
    require_organizer_admin
)
from app.models.user import User
from app.models.organizer import Organizer
from app.models.organizer_member import OrganizerMember
from app.schemas.organizer import (
    OrganizerCreate,
    OrganizerUpdate,
    OrganizerResponse,
    OrganizerWithMembersResponse
)
from app.services.organizer_service import OrganizerService
from app.services.organizer_member_service import OrganizerMemberService

router = APIRouter()


@router.post(
    "/",
    response_model=OrganizerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat organizer baru"
)
async def create_organizer(
    organizer_data: OrganizerCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Buat organizer baru.
    User yang membuat akan otomatis menjadi ORGANIZER_ADMIN.
    """
    organizer = await OrganizerService.create_organizer(
        db, organizer_data, current_user.id
    )
    return organizer


@router.get(
    "/my-organizers",
    response_model=List[OrganizerWithMembersResponse],
    summary="Get daftar organizer user"
)
async def get_my_organizers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """
    Get semua organizer dimana user adalah member aktif.
    """
    organizers = await OrganizerService.get_user_organizers(
        db, current_user.id, skip, limit
    )
    
    # Tambahkan info role user di setiap organizer
    result = []
    for org in organizers:
        member = await OrganizerMemberService.get_member(
            db, org.id, current_user.id
        )
        org_dict = OrganizerResponse.model_validate(org).model_dump()
        org_dict['user_role'] = member.role if member else None
        result.append(org_dict)
    
    return result


@router.get(
    "/{organizer_id}",
    response_model=OrganizerResponse,
    summary="Get detail organizer"
)
async def get_organizer(
    organizer: Annotated[Organizer, Depends(get_organizer_by_id)]
):
    """Get detail organizer by ID"""
    return organizer


@router.get(
    "/slug/{slug}",
    response_model=OrganizerResponse,
    summary="Get organizer by slug"
)
async def get_organizer_by_slug(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get organizer by slug"""
    organizer = await OrganizerService.get_organizer_by_slug(db, slug)
    return organizer


@router.patch(
    "/{organizer_id}",
    response_model=OrganizerResponse,
    summary="Update organizer"
)
async def update_organizer(
    organizer_id: int,
    update_data: OrganizerUpdate,
    _: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    organizer: Annotated[Organizer, Depends(get_organizer_by_id)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update organizer.
    Hanya ORGANIZER_ADMIN yang bisa.
    """
    updated_organizer = await OrganizerService.update_organizer(
        db, organizer, update_data
    )
    return updated_organizer


@router.delete(
    "/{organizer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organizer"
)
async def delete_organizer(
    organizer_id: int,
    _: Annotated[OrganizerMember, Depends(require_organizer_admin)],
    organizer: Annotated[Organizer, Depends(get_organizer_by_id)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete (suspend) organizer.
    Hanya ORGANIZER_ADMIN yang bisa.
    """
    await OrganizerService.delete_organizer(db, organizer)
    return None