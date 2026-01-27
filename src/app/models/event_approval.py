import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATETIME
from app.db.base import Base


class ApprovalStatus(str, enum.Enum):
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class EventApproval(Base):
    __tablename__ = "event_approvals"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    event_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('events.id'),
        nullable=False
    )

    submitted_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        nullable=False
    )

    decided_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        ENUM(ApprovalStatus, name='approval_status'),
        default='submitted',
        nullable=False
    )

    notes: Mapped[str] = mapped_column(
        VARCHAR(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    event = relationship(
        'Event',
        back_populates='approvals'
    )

    submitter = relationship(
        'User',
        foreign_keys=[submitted_by],
        back_populates='submitted_approvals'
    )

    decider = relationship(
        'User',
        foreign_keys=[decided_by],
        back_populates='decided_approvals'
    )
