from datetime import datetime

from pydantic import BaseModel, Field


class CrmUserCreate(BaseModel):
    username: str | None = Field(default=None, max_length=64)
    name: str | None = Field(default=None, max_length=128)
    nickname: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    parent_id: int | None = None
    parent_code: str | None = Field(default=None, max_length=64)
    role_type: str = Field(default="customer", max_length=32)
    certification_status: str = Field(default="pending", max_length=32)
    status: str = Field(default="active", max_length=32)
    remark: str | None = None


class CrmUserUpdate(CrmUserCreate):
    pass


class CrmUserStatusUpdate(BaseModel):
    status: str = Field(max_length=32)


class CrmUserRead(BaseModel):
    id: int
    username: str | None = None
    name: str | None = None
    nickname: str | None = None
    phone: str | None = None
    email: str | None = None
    parent_id: int | None = None
    parent_name: str | None = None
    parent_code: str | None = None
    role_type: str
    certification_status: str
    status: str
    remark: str | None = None
    mt5_login: str | None = None
    parent_mt5_login: str | None = None
    created_at: datetime
