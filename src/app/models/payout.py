import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.mysql import BIGINT, ENUM, DATETIME, DECIMAL
from app.db.base import Base


class PayoutStatus(str, enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    PAID = 'paid'
    FAILED = 'failed'


class Payout(Base):
    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    organizer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('organizers.id'),
        nullable=False
    )

    period_start: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    period_end: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    gross_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    fee_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    net_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(PayoutStatus, name='payout_status'),
        default='pending',
        nullable=False
    )

    paid_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    organizer = relationship(
        'Organizer',
        back_populates='payouts'
    )

    payout_lines = relationship(
        'PayoutLine',
        back_populates='payout',
        cascade='all, delete-orphan'
    )
