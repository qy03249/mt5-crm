from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.admin.models import utc_now


class CrmUser(Base):
    __tablename__ = "crm_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("crm_users.id"), nullable=True)
    parent_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role_type: Mapped[str] = mapped_column(String(32), default="customer")
    certification_status: Mapped[str] = mapped_column(String(32), default="pending")
    status: Mapped[str] = mapped_column(String(32), default="active")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    parent: Mapped["CrmUser | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["CrmUser"]] = relationship(back_populates="parent")
    profile: Mapped["CrmUserProfile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class CrmUserProfile(Base):
    __tablename__ = "crm_user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("crm_users.id"), primary_key=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education: Mapped[str | None] = mapped_column(String(64), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    id_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    id_front_file_id: Mapped[int | None] = mapped_column(nullable=True)
    id_back_file_id: Mapped[int | None] = mapped_column(nullable=True)
    proof_file_id: Mapped[int | None] = mapped_column(nullable=True)

    user: Mapped[CrmUser] = relationship(back_populates="profile")
