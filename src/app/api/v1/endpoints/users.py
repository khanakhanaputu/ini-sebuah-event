from typing import Any, List, Annotated
# EmailStr gak perlu diimport karena gak dipake di file ini
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

# --- Dependencies ---
from app.deps.db import get_db
from app.deps.auth import get_current_user, get_current_active_superuser

# --- Models & Schemas ---
from app.models.user import User, UserStatus, PlatformRole
from app.models.organizer_member import OrganizerMember  # <-- TAMBAHKAN INI
from app.schemas.user import UserUpdate, UserResponse, UserPublicResponse, UserStatusUpdate


router = APIRouter()

# ==========================================
# 1. GET MY PROFILE
# ==========================================
@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Ambil data user yang sedang login"
)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Endpoint ini dipakai Frontend untuk:
    1. Menampilkan "Halo, Budi".
    2. Mengecek apakah `phone_number` masih null (jika null -> redirect ke onboarding).
    """
    return current_user


# ==========================================
# 2. UPDATE MY PROFILE (ONBOARDING)
# ==========================================
@router.patch(
    "/me", 
    response_model=UserResponse,
    summary="Update data diri sendiri (No HP & Nama)"
)
async def update_user_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    User mengupdate profilnya sendiri.
    Biasanya dipanggil saat pertama kali login Google (Onboarding).
    """

    # --- A. Validasi Unik No HP (PENTING) ---
    if payload.phone_number and payload.phone_number != current_user.phone_number:
        stmt = select(User).where(
            User.phone_number == payload.phone_number,
            User.id != current_user.id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Nomor HP ini sudah digunakan oleh akun lain."
            )

    # --- B. Update Field ---
    updated = False
    
    if payload.full_name:
        current_user.full_name = payload.full_name
        updated = True
        
    if payload.phone_number:
        current_user.phone_number = payload.phone_number
        updated = True

    # --- C. Simpan ke DB ---
    if updated:
        try:
            db.add(current_user)
            await db.commit()
            await db.refresh(current_user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    return current_user


# ==========================================
# 3. ADMIN: BAN / UNBAN USER
# ==========================================
@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Ubah status user (Ban/Unban) - Khusus Super Admin"
)
async def change_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_admin: User = Depends(get_current_active_superuser), 
    db: AsyncSession = Depends(get_db),
):
    """
    Hanya Platform Admin yang bisa mengubah status user lain.
    Contoh: Mengubah 'active' menjadi 'banned'.
    """
    
    # 1. Cari User target berdasarkan ID
    target_user = await db.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )

    # 2. Proteksi: Jangan biarkan Admin nge-ban sesama Admin
    if target_user.role == PlatformRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sesama Super Admin tidak boleh saling menjatuhkan! 😤"
        )

    # 3. Update Status
    target_user.user_status = payload.user_status
    
    # 4. Simpan
    db.add(target_user)
    await db.commit()
    await db.refresh(target_user)

    return target_user


# ==========================================
# 4. SEARCH USERS
# ==========================================
@router.get(
    "/search",
    response_model=List[UserPublicResponse],
    summary="Search users"
)
async def search_users(
    q: str = Query(..., min_length=2, description="Search query (name or email)"),
    organizer_id: int | None = Query(None, description="Exclude users already in this organizer"),
    limit: int = Query(10, le=50, description="Max results"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
    """
    Search users by name or email.
    
    - Jika `organizer_id` diberikan, akan exclude user yang sudah jadi member organizer tersebut
    - Case-insensitive search
    - Max 50 results
    """
    
    # Base query
    query = select(User).where(
        or_(
            User.full_name.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%")
        )
    ).limit(limit)
    
    # Exclude users yang sudah jadi member organizer tertentu
    if organizer_id:
        # Subquery untuk get user_ids yang sudah member
        member_subquery = select(OrganizerMember.user_id).where(
            OrganizerMember.organizer_id == organizer_id
        )
        
        query = query.where(
            User.id.not_in(member_subquery)
        )
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users