import enum
from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Date
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME
from app.db.base import Base


class Role(str, enum.Enum):
    ORGANIZER_ADMIN = 'organizer_admin'
    FINANCE = 'finance'
    GATE = 'gate'
    VIEWER = 'viewer'

class Status(str, enum.Enum):
    ACTIVE = 'acitve'
    INACTIVE = 'inactive'

class OrganizerMember(Base):
    __tablename__ = 'organizer_members'

    organizer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('organizers.id', ondelete="CASCADE"),
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=True
    )

    role: Mapped[str] = mapped_column(
        ENUM(Role, name='role'),
        nullable=False,
    )
    
    status: Mapped[str] = mapped_column(
        ENUM(Status, name='status'),
        default='active'
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        'User',
        back_populates='organizer_member',
    )

    organizer = relationship(
        'Organizer',
        back_populates='organizer_member'
    )

