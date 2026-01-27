import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, TEXT, CHAR, BOOLEAN
from app.db.base import Base


class EventVisibility(str, enum.Enum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    PUBLISHED = 'published'
    REJECTED = 'rejected'
    ENDED = 'ended'


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    organizer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('organizers.id'),
        nullable=False
    )

    created_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        VARCHAR(160),
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        VARCHAR(120),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        TEXT,
        nullable=True
    )

    venue_name: Mapped[str] = mapped_column(
        VARCHAR(160),
        nullable=True
    )

    venue_address: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=True
    )

    start_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    end_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    visibility: Mapped[str] = mapped_column(
        ENUM(EventVisibility, name='event_visibility'),
        default='draft',
        nullable=False
    )

    is_free: Mapped[bool] = mapped_column(
        BOOLEAN,
        default=False,
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        CHAR(3),
        default='IDR',
        nullable=False
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

    # Relationships
    organizer = relationship(
        'Organizer',
        back_populates='events'
    )

    creator = relationship(
        'User',
        foreign_keys=[created_by],
        back_populates='created_events'
    )

    approvals = relationship(
        'EventApproval',
        back_populates='event',
        cascade='all, delete-orphan'
    )

    ticket_types = relationship(
        'TicketType',
        back_populates='event',
        cascade='all, delete-orphan'
    )

    orders = relationship(
        'Order',
        back_populates='event',
        cascade='all, delete-orphan'
    )

    promo_codes = relationship(
        'PromoCode',
        back_populates='event',
        cascade='all, delete-orphan'
    )
