import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME, JSON as MYSQL_JSON
from app.db.base import Base


class CheckinResult(str, enum.Enum):
    OK = 'ok'
    DUPLICATE = 'duplicate'
    INVALID = 'invalid'
    BLOCKED = 'blocked'


class Checkin(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('tickets.id'),
        nullable=False
    )

    gate_user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        nullable=False
    )

    scanned_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    result: Mapped[str] = mapped_column(
        ENUM(CheckinResult, name='checkin_result'),
        nullable=False
    )

    device_id: Mapped[str] = mapped_column(
        VARCHAR(80),
        nullable=True
    )

    meta: Mapped[dict] = mapped_column(
        MYSQL_JSON,
        nullable=True
    )

    # Relationships
    ticket = relationship(
        'Ticket',
        back_populates='checkins'
    )

    gate_user = relationship(
        'User',
        back_populates='checkins'
    )
