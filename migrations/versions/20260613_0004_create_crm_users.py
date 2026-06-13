"""create crm users

Revision ID: 20260613_0004
Revises: 20260613_0003
Create Date: 2026-06-13 22:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260613_0004"
down_revision: str | None = "20260613_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 创建 CRM 用户表，对应“客户 / CRM用户、CRM上下级、黑名单”页面。
    op.create_table(
        "crm_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("username", sa.String(length=64), nullable=True, comment="用户名"),
        sa.Column("name", sa.String(length=128), nullable=True, comment="姓名"),
        sa.Column("nickname", sa.String(length=128), nullable=True, comment="昵称"),
        sa.Column("phone", sa.String(length=64), nullable=True, comment="手机"),
        sa.Column("email", sa.String(length=255), nullable=True, comment="邮箱"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="上级CRM用户ID"),
        sa.Column("parent_code", sa.String(length=64), nullable=True, comment="上级代码"),
        sa.Column(
            "role_type",
            sa.String(length=32),
            nullable=False,
            comment="用户角色：customer/agent/ib",
        ),
        sa.Column(
            "certification_status",
            sa.String(length=32),
            nullable=False,
            comment="认证状态：pending/approved/rejected",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            comment="用户状态：active/disabled/blacklisted",
        ),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.ForeignKeyConstraint(["parent_id"], ["crm_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="CRM用户表",
    )
    op.create_index("ix_crm_users_email", "crm_users", ["email"])
    op.create_index("ix_crm_users_phone", "crm_users", ["phone"])

    # 创建 CRM 用户资料表，用于保存认证资料基础字段。
    op.create_table(
        "crm_user_profiles",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="CRM用户ID"),
        sa.Column("gender", sa.String(length=16), nullable=True, comment="性别"),
        sa.Column("country", sa.String(length=64), nullable=True, comment="国家地区"),
        sa.Column("address", sa.String(length=255), nullable=True, comment="居住地"),
        sa.Column("education", sa.String(length=64), nullable=True, comment="学历"),
        sa.Column("birthday", sa.Date(), nullable=True, comment="出生日期"),
        sa.Column("occupation", sa.String(length=128), nullable=True, comment="职业"),
        sa.Column("id_type", sa.String(length=32), nullable=True, comment="证件类型"),
        sa.Column("id_number", sa.String(length=128), nullable=True, comment="证件号码"),
        sa.Column("id_front_file_id", sa.Integer(), nullable=True, comment="证件正面文件ID"),
        sa.Column("id_back_file_id", sa.Integer(), nullable=True, comment="证件反面文件ID"),
        sa.Column("proof_file_id", sa.Integer(), nullable=True, comment="身份证明文件ID"),
        sa.ForeignKeyConstraint(["user_id"], ["crm_users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
        comment="CRM用户认证资料表",
    )

    # 写入两条演示客户数据，方便本地页面立即验证 CRM 用户列表。
    op.execute(
        """
        INSERT INTO crm_users (
            id, username, name, nickname, phone, email, parent_id, parent_code,
            role_type, certification_status, status, remark, created_at, updated_at
        ) VALUES
        (
            1, 'agent001', '上级代理', '代理A', '13800000000', 'agent@example.test',
            NULL, 'AG001', 'agent', 'approved', 'active', '演示上级代理', NOW(), NOW()
        ),
        (
            2, 'client001', '张三', '客户一号', '13900000000', 'client@example.test',
            1, 'AG001', 'customer', 'pending', 'active', '首个CRM客户', NOW(), NOW()
        )
        """
    )


def downgrade() -> None:
    # 回滚 CRM 用户相关表。
    op.drop_table("crm_user_profiles")
    op.drop_index("ix_crm_users_phone", table_name="crm_users")
    op.drop_index("ix_crm_users_email", table_name="crm_users")
    op.drop_table("crm_users")
