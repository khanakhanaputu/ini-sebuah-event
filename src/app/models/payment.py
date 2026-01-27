import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, DECIMAL, JSON as MYSQL_JSON
from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    INITIATED = 'initiated'
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    EXPIRED = 'expired'
    REFUNDED = 'refunded'


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('orders.id'),
        nullable=False
    )

    provider: Mapped[str] = mapped_column(
        VARCHAR(60),
        nullable=False
    )

    method: Mapped[str] = mapped_column(
        VARCHAR(60),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(PaymentStatus, name='payment_status'),
        default='initiated',
        nullable=False
    )

    payment_ref: Mapped[str] = mapped_column(
        VARCHAR(191),
        nullable=True
    )

    paid_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=True
    )

    provider_payload: Mapped[dict] = mapped_column(
        MYSQL_JSON,
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
    order = relationship(
        'Order',
        back_populates='payments'
    )
