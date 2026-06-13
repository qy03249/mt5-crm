"""create admin auth tables

Revision ID: 20260613_0001
Revises: None
Create Date: 2026-06-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260613_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("username", sa.String(length=64), nullable=False, comment="后台登录账号"),
        sa.Column("password_hash", sa.String(length=255), nullable=False, comment="密码哈希"),
        sa.Column("display_name", sa.String(length=64), nullable=False, comment="后台显示名称"),
        sa.Column("email", sa.String(length=255), nullable=True, comment="管理员邮箱"),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            comment="账号状态：active/disabled",
        ),
        sa.Column("last_login_at", sa.DateTime(), nullable=True, comment="最后登录时间"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        comment="后台管理员账号表",
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"], unique=True)

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("code", sa.String(length=64), nullable=False, comment="角色编码"),
        sa.Column("name", sa.String(length=64), nullable=False, comment="角色名称"),
        sa.Column("description", sa.String(length=255), nullable=True, comment="角色说明"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        comment="后台角色表",
    )
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("code", sa.String(length=128), nullable=False, comment="权限编码"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="权限名称"),
        sa.Column(
            "type",
            sa.String(length=32),
            nullable=False,
            comment="权限类型：menu/button/data",
        ),
        sa.Column("path", sa.String(length=255), nullable=True, comment="前端路由或接口路径"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父级权限ID"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.ForeignKeyConstraint(["parent_id"], ["permissions.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="后台权限表",
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)

    op.create_table(
        "admin_user_roles",
        sa.Column("admin_user_id", sa.Integer(), nullable=False, comment="后台账号ID"),
        sa.Column("role_id", sa.Integer(), nullable=False, comment="角色ID"),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("admin_user_id", "role_id"),
        comment="后台账号和角色关系表",
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False, comment="角色ID"),
        sa.Column("permission_id", sa.Integer(), nullable=False, comment="权限ID"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
        comment="角色和权限关系表",
    )


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("admin_user_roles")
    op.drop_index("ix_permissions_code", table_name="permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_code", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
