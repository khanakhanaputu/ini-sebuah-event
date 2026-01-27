import enum
from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Date
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME
from app.db.base import Base

class OrganizerStatus(str, enum.Enum):
    PENDING = 'pending'
    VERIFIED = 'verified'
    SUSPENDED = 'suspended'

class Organizer(Base):
    __tablename__ = 'organizers'

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
        )
    
    name: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
        unique=True
    )

    slug: Mapped[str] = mapped_column(
        VARCHAR(100),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(OrganizerStatus, name='organizer_status'),
        default='PENDING'
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
        back_populates='organizer'
    )

    events = relationship(
        'Event',
        back_populates='organizer'
    )

    orders = relationship(
        'Order',
        back_populates='organizer'
    )

    payouts = relationship(
        'Payout',
        back_populates='organizer'
    )

    promo_codes = relationship(
        'PromoCode',
        back_populates='organizer'
    )
