import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, DECIMAL, INTEGER
from app.db.base import Base


class TicketStatus(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class TicketType(Base):
    __tablename__ = "ticket_types"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    event_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('events.id'),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        VARCHAR(120),
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    quota: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False
    )

    sold_count: Mapped[int] = mapped_column(
        INTEGER,
        default=0,
        nullable=False
    )

    sale_start_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    sale_end_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False
    )

    max_per_order: Mapped[int] = mapped_column(
        INTEGER,
        default=10,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        ENUM(TicketStatus, name='ticket_status'),
        default='active',
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
    event = relationship(
        'Event',
        back_populates='ticket_types'
    )

    order_items = relationship(
        'OrderItem',
        back_populates='ticket_type',
        cascade='all, delete-orphan'
    )
