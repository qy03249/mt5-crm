from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.admin.models import AdminUser, Permission, Role
from app.modules.admin.schemas import (
    AdminAccountCreate,
    AdminAccountRead,
    PermissionCreate,
    PermissionRead,
    RoleCreate,
    RolePermissionUpdate,
    RolePermissionUpdateResult,
    RoleRead,
)
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.security import hash_password

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)],
)


def role_to_read(role: Role) -> RoleRead:
    return RoleRead(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        permission_count=len(role.permissions),
    )


def permission_to_read(permission: Permission) -> PermissionRead:
    return PermissionRead(
        id=permission.id,
        code=permission.code,
        name=permission.name,
        type=permission.type,
        path=permission.path,
        parent_id=permission.parent_id,
    )


def account_to_read(account: AdminUser) -> AdminAccountRead:
    return AdminAccountRead(
        id=account.id,
        username=account.username,
        display_name=account.display_name,
        email=account.email,
        status=account.status,
        roles=[role_to_read(role) for role in account.roles],
    )


def current_user_permissions_by_type(user: AdminUser, permission_type: str) -> list[PermissionRead]:
    permissions_by_code = {
        permission.code: permission
        for role in user.roles
        for permission in role.permissions
        if permission.type == permission_type
    }
    permissions = sorted(permissions_by_code.values(), key=lambda item: item.id)
    return [permission_to_read(permission) for permission in permissions]


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Annotated[Session, Depends(get_db)]) -> RoleRead:
    existing = db.scalar(select(Role).where(Role.code == payload.code))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Role code already exists")

    role = Role(code=payload.code, name=payload.name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role_to_read(role)


@router.get("/roles", response_model=list[RoleRead])
def list_roles(db: Annotated[Session, Depends(get_db)]) -> list[RoleRead]:
    roles = db.scalars(select(Role).options(selectinload(Role.permissions))).all()
    return [role_to_read(role) for role in roles]


@router.post(
    "/permissions",
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    payload: PermissionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PermissionRead:
    existing = db.scalar(select(Permission).where(Permission.code == payload.code))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Permission code already exists")

    permission = Permission(
        code=payload.code,
        name=payload.name,
        type=payload.type,
        path=payload.path,
        parent_id=payload.parent_id,
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission_to_read(permission)


@router.get("/permissions", response_model=list[PermissionRead])
def list_permissions(db: Annotated[Session, Depends(get_db)]) -> list[PermissionRead]:
    permissions = db.scalars(select(Permission)).all()
    return [permission_to_read(permission) for permission in permissions]


@router.get("/permissions/menus", response_model=list[PermissionRead])
def list_current_user_menu_permissions(
    current_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> list[PermissionRead]:
    return current_user_permissions_by_type(current_user, "menu")


@router.get("/permissions/buttons", response_model=list[PermissionRead])
def list_current_user_button_permissions(
    current_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> list[PermissionRead]:
    return current_user_permissions_by_type(current_user, "button")


@router.put("/roles/{role_id}/permissions", response_model=RolePermissionUpdateResult)
def update_role_permissions(
    role_id: int,
    payload: RolePermissionUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> RolePermissionUpdateResult:
    role = db.scalar(select(Role).where(Role.id == role_id).options(selectinload(Role.permissions)))
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    permissions = db.scalars(
        select(Permission).where(Permission.id.in_(payload.permission_ids))
    ).all()
    if len(permissions) != len(set(payload.permission_ids)):
        raise HTTPException(status_code=400, detail="Some permissions do not exist")

    role.permissions = list(permissions)
    db.commit()
    db.refresh(role)
    return RolePermissionUpdateResult(
        id=role.id,
        code=role.code,
        name=role.name,
        permission_count=len(role.permissions),
    )


@router.post("/accounts", response_model=AdminAccountRead, status_code=status.HTTP_201_CREATED)
def create_admin_account(
    payload: AdminAccountCreate,
    db: Annotated[Session, Depends(get_db)],
) -> AdminAccountRead:
    existing = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Username already exists")

    roles = db.scalars(select(Role).where(Role.id.in_(payload.role_ids))).all()
    if len(roles) != len(set(payload.role_ids)):
        raise HTTPException(status_code=400, detail="Some roles do not exist")

    account = AdminUser(
        username=payload.username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        email=str(payload.email) if payload.email else None,
        status="active",
    )
    account.roles = list(roles)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account_to_read(account)


@router.get("/accounts", response_model=list[AdminAccountRead])
def list_admin_accounts(db: Annotated[Session, Depends(get_db)]) -> list[AdminAccountRead]:
    accounts = db.scalars(select(AdminUser).options(selectinload(AdminUser.roles))).all()
    return [account_to_read(account) for account in accounts]
