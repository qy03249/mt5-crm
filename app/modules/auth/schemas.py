from pydantic import BaseModel


class CurrentUserRoleRead(BaseModel):
    id: int
    code: str
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserRead(BaseModel):
    id: int
    username: str
    display_name: str
    email: str | None = None
    roles: list[CurrentUserRoleRead]
