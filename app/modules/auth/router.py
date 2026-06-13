from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.admin.models import AdminUser
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.schemas import (
    CurrentUserRead,
    CurrentUserRoleRead,
    LoginRequest,
    TokenResponse,
)
from app.modules.auth.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = db.scalar(
        select(AdminUser)
        .where(AdminUser.username == payload.username, AdminUser.status == "active")
        .options(selectinload(AdminUser.roles))
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=CurrentUserRead)
def read_current_user(
    current_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> CurrentUserRead:
    return CurrentUserRead(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        email=current_user.email,
        roles=[
            CurrentUserRoleRead(
                id=role.id,
                code=role.code,
                name=role.name,
            )
            for role in current_user.roles
        ],
    )
