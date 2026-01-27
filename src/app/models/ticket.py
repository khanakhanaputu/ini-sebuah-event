import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME
from app.db.base import Base


class TicketStatusEnum(str, enum.Enum):
    ISSUED = 'issued'
    CHECKED_IN = 'checked_in'
    VOID = 'void'
    REFUNDED = 'refunded'


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    order_item_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('order_items.id'),
        nullable=False
    )

    ticket_code: Mapped[str] = mapped_column(
        VARCHAR(80),
        unique=True,
        nullable=False
    )

    qr_token: Mapped[str] = mapped_column(
        VARCHAR(255),
        unique=True,
        nullable=False
    )

    attendee_name: Mapped[str] = mapped_column(
        VARCHAR(120),
        nullable=True
    )

    attendee_email: Mapped[str] = mapped_column(
        VARCHAR(191),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        ENUM(TicketStatusEnum, name='ticket_status_enum'),
        default='issued',
        nullable=False
    )

    issued_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    order_item = relationship(
        'OrderItem',
        back_populates='tickets'
    )

    checkins = relationship(
        'Checkin',
        back_populates='ticket',
        cascade='all, delete-orphan'
    )
