from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, DECIMAL, INTEGER
from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('orders.id'),
        nullable=False
    )

    ticket_type_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('ticket_types.id'),
        nullable=False
    )

    qty: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    order = relationship(
        'Order',
        back_populates='order_items'
    )

    ticket_type = relationship(
        'TicketType',
        back_populates='order_items'
    )

    tickets = relationship(
        'Ticket',
        back_populates='order_item',
        cascade='all, delete-orphan'
    )
