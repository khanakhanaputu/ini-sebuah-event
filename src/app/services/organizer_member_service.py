from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.organizer_member import OrganizerMember, Role, Status as MemberStatus
from app.models.user import User
from app.schemas.organizer_member import OrganizerMemberInvite, OrganizerMemberUpdate, OrganizerMemberInviteByEmail


class OrganizerMemberService:
    @staticmethod
    async def get_member(
        db: AsyncSession,
        organizer_id: int,
        user_id: int
    ) -> OrganizerMember | None:
        result = await db.execute(
            select(OrganizerMember).where(
                OrganizerMember.organizer_id == organizer_id,
                OrganizerMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def invite_member(
        db: AsyncSession,
        organizer_id: int,
        invite_data: OrganizerMemberInvite
    ) -> OrganizerMember:
        # Cek user exist
        user = await db.get(User, invite_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan"
            )
        
        # Cek apakah sudah member
        existing = await OrganizerMemberService.get_member(
            db, organizer_id, invite_data.user_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User sudah menjadi member organizer ini"
            )
        
        member = OrganizerMember(
            organizer_id=organizer_id,
            user_id=invite_data.user_id,
            role=invite_data.role,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def get_organizer_members(
        db: AsyncSession,
        organizer_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        query = (
            select(OrganizerMember)
            .where(OrganizerMember.organizer_id == organizer_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_member(
        db: AsyncSession,
        member: OrganizerMember,
        update_data: OrganizerMemberUpdate
    ) -> OrganizerMember:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(member, key, value)
        
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def remove_member(
        db: AsyncSession,
        member: OrganizerMember
    ):
        await db.delete(member)
        await db.commit()

    
    @staticmethod
    async def invite_by_email(
        db: AsyncSession,
        organizer_id: int,
        invite_data: OrganizerMemberInviteByEmail
    ) -> OrganizerMember:
    
        # 1. Cari user by email
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == invite_data.email)
        )
        user = result.scalar_one_or_none()
        
        # 2. Kalau user tidak ada, reject
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User dengan email {invite_data.email} belum terdaftar. Minta mereka register dulu."
            )
        
        # 3. Cek apakah sudah member
        existing = await OrganizerMemberService.get_member(
            db, organizer_id, user.id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User sudah menjadi member organizer ini"
            )
        
        # 4. Add sebagai member
        member = OrganizerMember(
            organizer_id=organizer_id,
            user_id=user.id,
            role=invite_data.role,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member