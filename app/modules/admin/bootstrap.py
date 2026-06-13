from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.admin.models import AdminUser, Permission, Role
from app.modules.auth.security import hash_password

DEFAULT_ADMIN_PERMISSIONS = [
    ("dashboard.view", "首页", "menu", "/home"),
    ("task.view", "任务", "menu", "/task"),
    ("client.view", "客户", "menu", "/client"),
    ("report.view", "报表", "menu", "/report"),
    ("record.view", "记录", "menu", "/record"),
    ("setting.view", "设置", "menu", "/setting"),
    ("admin.account.manage", "后台账户管理", "button", "/setting/permissions/account"),
    ("admin.role.manage", "角色权限管理", "button", "/setting/permissions/account"),
]


def ensure_initial_admin(
    db: Session,
    *,
    username: str,
    password: str,
    email: str,
) -> AdminUser:
    existing_admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if existing_admin is not None:
        return existing_admin

    role = db.scalar(select(Role).where(Role.code == "admin"))
    if role is None:
        role = Role(code="admin", name="管理员", description="系统超级管理员")
        db.add(role)
        db.flush()

    permissions: list[Permission] = []
    for code, name, permission_type, path in DEFAULT_ADMIN_PERMISSIONS:
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, name=name, type=permission_type, path=path)
            db.add(permission)
            db.flush()
        permissions.append(permission)

    role.permissions = permissions

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
