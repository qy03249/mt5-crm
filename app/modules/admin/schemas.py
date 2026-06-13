from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    description: str | None = None


class RoleRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    permission_count: int = 0


class PermissionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=32)
    path: str | None = None
    parent_id: int | None = None


class PermissionRead(BaseModel):
    id: int
    code: str
    name: str
    type: str
    path: str | None = None
    parent_id: int | None = None


class RolePermissionUpdate(BaseModel):
    permission_ids: list[int]


class RolePermissionUpdateResult(BaseModel):
    id: int
    code: str
    name: str
    permission_count: int


class AdminAccountCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=64)
    email: str | None = None
    role_ids: list[int] = Field(default_factory=list)


class AdminAccountRead(BaseModel):
    id: int
    username: str
    display_name: str
    email: str | None = None
    status: str
    roles: list[RoleRead] = Field(default_factory=list)
