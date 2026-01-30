import enum
from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Date
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, ENUM, DATE, DATETIME
from app.db.base import Base


class Gender(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey('users.id'),
        primary_key=True,
    )

    full_name: Mapped[str] = mapped_column(
        VARCHAR(120),
        nullable=True
    )

    phone: Mapped[str] = mapped_column(
        VARCHAR(30),
        nullable=True
    )

    gender: Mapped[str] = mapped_column(
        ENUM(Gender, name='gender'),
        nullable=True
    )

    birth_date: Mapped[date] = mapped_column(
        DATE,
        nullable=True
    )

    avatar_url: Mapped[str] = mapped_column(
        VARCHAR(255),
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


