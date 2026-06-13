from datetime import datetime

from pydantic import BaseModel


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
