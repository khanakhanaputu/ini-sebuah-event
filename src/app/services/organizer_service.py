from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.organizer import Organizer, OrganizerStatus
from app.models.organizer_member import OrganizerMember, Role, Status as MemberStatus
from app.schemas.organizer import OrganizerCreate, OrganizerUpdate
from slugify import slugify


class OrganizerService:
    @staticmethod
    async def create_organizer(
        db: AsyncSession,
        organizer_data: OrganizerCreate,
        creator_user_id: int
    ) -> Organizer:
        """Buat organizer baru dan set creator sebagai admin"""
        
        # Generate slug dari name
        base_slug = slugify(organizer_data.name)
        slug = base_slug
        
        # Cek slug unique
        counter = 1
        while True:
            result = await db.execute(
                select(Organizer).where(Organizer.slug == slug)
            )
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Buat organizer
        organizer = Organizer(
            name=organizer_data.name,
            slug=slug,
            status=OrganizerStatus.PENDING
        )
        db.add(organizer)
        await db.flush()
        
        # Tambahkan creator sebagai admin
        member = OrganizerMember(
            organizer_id=organizer.id,
            user_id=creator_user_id,
            role=Role.ORGANIZER_ADMIN,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        await db.commit()
        await db.refresh(organizer)
        
        return organizer

    @staticmethod
    async def get_organizer_by_id(
        db: AsyncSession,
        organizer_id: int
    ) -> Organizer:
        organizer = await db.get(Organizer, organizer_id)
        if not organizer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer tidak ditemukan"
            )
        return organizer

    @staticmethod
    async def get_organizer_by_slug(
        db: AsyncSession,
        slug: str
    ) -> Organizer:
        result = await db.execute(
            select(Organizer).where(Organizer.slug == slug)
        )
        organizer = result.scalar_one_or_none()
        if not organizer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer tidak ditemukan"
            )
        return organizer

    @staticmethod
    async def get_user_organizers(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        """Get semua organizer yang user adalah member-nya"""
        query = (
            select(Organizer)
            .join(OrganizerMember)
            .where(
                OrganizerMember.user_id == user_id,
                OrganizerMember.status == MemberStatus.ACTIVE
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_organizer(
        db: AsyncSession,
        organizer: Organizer,
        update_data: OrganizerUpdate
    ) -> Organizer:
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Jika name diupdate, regenerate slug
        if 'name' in update_dict:
            base_slug = slugify(update_dict['name'])
            slug = base_slug
            counter = 1
            while True:
                result = await db.execute(
                    select(Organizer).where(
                        Organizer.slug == slug,
                        Organizer.id != organizer.id
                    )
                )
                if not result.scalar_one_or_none():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
            update_dict['slug'] = slug
        
        for key, value in update_dict.items():
            setattr(organizer, key, value)
        
        await db.commit()
        await db.refresh(organizer)
        return organizer

    @staticmethod
    async def delete_organizer(
        db: AsyncSession,
        organizer: Organizer
    ):
        """Soft delete dengan set status SUSPENDED"""
        organizer.status = OrganizerStatus.SUSPENDED
        await db.commit()