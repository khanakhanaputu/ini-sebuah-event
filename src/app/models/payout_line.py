from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, DECIMAL
from app.db.base import Base


class PayoutLine(Base):
    __tablename__ = "payout_lines"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    payout_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('payouts.id'),
        nullable=False
    )

    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('orders.id'),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    payout = relationship(
        'Payout',
        back_populates='payout_lines'
    )

    order = relationship(
        'Order',
        back_populates='payout_lines'
    )
