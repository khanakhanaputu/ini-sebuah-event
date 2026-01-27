import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, DECIMAL, CHAR
from app.db.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    EXPIRED = 'expired'
    CANCELED = 'canceled'
    REFUNDED = 'refunded'


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    event_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('events.id'),
        nullable=False
    )

    organizer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('organizers.id'),
        nullable=False
    )

    buyer_user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        nullable=False
    )

    order_code: Mapped[str] = mapped_column(
        VARCHAR(40),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(OrderStatus, name='order_status'),
        default='pending',
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        CHAR(3),
        default='IDR',
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    discount_total: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        default=0,
        nullable=False
    )

    fee_total: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        default=0,
        nullable=False
    )

    grand_total: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=True
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

    updated_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    event = relationship(
        'Event',
        back_populates='orders'
    )

    organizer = relationship(
        'Organizer',
        back_populates='orders'
    )

    buyer = relationship(
        'User',
        back_populates='orders'
    )

    order_items = relationship(
        'OrderItem',
        back_populates='order',
        cascade='all, delete-orphan'
    )

    payments = relationship(
        'Payment',
        back_populates='order',
        cascade='all, delete-orphan'
    )

    payout_lines = relationship(
        'PayoutLine',
        back_populates='order',
        cascade='all, delete-orphan'
    )
