from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.admin.models import AdminUser, Permission, Role
from app.modules.auth.security import hash_password

DEFAULT_ADMIN_PERMISSIONS = [
    ("dashboard.view", "首页", "menu", "/home", None),
    ("task.view", "任务", "menu", "/task", None),
    ("client.view", "客户", "menu", "/client", None),
    ("report.view", "报表", "menu", "/report", None),
    ("record.view", "记录", "menu", "/record", None),
    ("setting.view", "设置", "menu", "/setting", None),
    (
        "setting.backend_permission.view",
        "后台权限",
        "menu",
        None,
        "setting.view",
    ),
    (
        "admin.account.view",
        "后台账户",
        "menu",
        "/setting/permissions/account",
        "setting.backend_permission.view",
    ),
    (
        "admin.role.view",
        "角色权限",
        "menu",
        "/setting/permissions/role",
        "setting.backend_permission.view",
    ),
    (
        "admin.account.manage",
        "后台账户管理",
        "button",
        "/setting/permissions/account",
        "admin.account.view",
    ),
    (
        "admin.role.manage",
        "角色权限管理",
        "button",
        "/setting/permissions/role",
        "admin.role.view",
    ),
]


def sync_default_permissions(db: Session) -> list[Permission]:
    permissions_by_code: dict[str, Permission] = {}
    for code, name, permission_type, path, _parent_code in DEFAULT_ADMIN_PERMISSIONS:
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, name=name, type=permission_type, path=path)
            db.add(permission)
            db.flush()
        else:
            permission.name = name
            permission.type = permission_type
            permission.path = path
        permissions_by_code[code] = permission

    for code, _name, _permission_type, _path, parent_code in DEFAULT_ADMIN_PERMISSIONS:
        permission = permissions_by_code[code]
        parent = permissions_by_code.get(parent_code) if parent_code else None
        permission.parent_id = parent.id if parent else None

    return list(permissions_by_code.values())


def ensure_initial_admin(
    db: Session,
    *,
    username: str,
    password: str,
    email: str,
) -> AdminUser:
    role = db.scalar(select(Role).where(Role.code == "admin"))
    if role is None:
        role = Role(code="admin", name="管理员", description="系统超级管理员")
        db.add(role)
        db.flush()

    permissions = sync_default_permissions(db)
    role.permissions = permissions

    existing_admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if existing_admin is not None:
        db.commit()
        db.refresh(existing_admin)
        return existing_admin

    admin = AdminUser(
        username=username,
        password_hash=hash_password(password),
        display_name="系统管理员",
        email=email,
        status="active",
    )
    admin.roles = [role]
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
