import enum
from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Date
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME
from app.db.base import Base


class PlatformRole(str, enum.Enum):
    PLATFORM_ADMIN = 'platform_admin'
    USER = 'user'

class UserStatus(str, enum.Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    BANNED = 'banned'

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
    )

    google_id: Mapped[str] = mapped_column(
        VARCHAR(255),
        unique=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        VARCHAR(100),
        unique=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=True
    )

    avatar: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=True
    )

    role: Mapped[str] = mapped_column(
        ENUM(PlatformRole, name='platform_roles'),
        nullable=False,
        default='user'
    )

    phone_number: Mapped[str] = mapped_column(
        VARCHAR(20),
        nullable=True
    )

    user_status: Mapped[str] = mapped_column(
        ENUM(UserStatus, name='user_status'),
        nullable=False,
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

    organizer_member = relationship(
        'OrganizerMember',
        back_populates='user'
    )


    created_events = relationship(
        'Event',
        foreign_keys='Event.created_by',
        back_populates='creator'
    )

    submitted_approvals = relationship(
        'EventApproval',
        foreign_keys='EventApproval.submitted_by',
        back_populates='submitter'
    )

    decided_approvals = relationship(
        'EventApproval',
        foreign_keys='EventApproval.decided_by',
        back_populates='decider'
    )

    orders = relationship(
        'Order',
        back_populates='buyer'
    )

    checkins = relationship(
        'Checkin',
        back_populates='gate_user'
    )
