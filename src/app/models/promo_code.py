import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, DECIMAL, INTEGER
from app.db.base import Base


class PromoCodeType(str, enum.Enum):
    PERCENT = 'percent'
    AMOUNT = 'amount'


class PromoCodeStatus(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    organizer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('organizers.id'),
        nullable=False
    )

    event_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('events.id'),
        nullable=True
    )

    code: Mapped[str] = mapped_column(
        VARCHAR(40),
        unique=True,
        nullable=False
    )

    type: Mapped[str] = mapped_column(
        ENUM(PromoCodeType, name='promo_code_type'),
        nullable=False
    )

    value: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    quota: Mapped[int] = mapped_column(
        INTEGER,
        nullable=True
    )

    used_count: Mapped[int] = mapped_column(
        INTEGER,
        default=0,
        nullable=False
    )

    valid_from: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    valid_until: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(PromoCodeStatus, name='promo_code_status'),
        default='active',
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    organizer = relationship(
        'Organizer',
        back_populates='promo_codes'
    )

    event = relationship(
        'Event',
        back_populates='promo_codes'
    )
