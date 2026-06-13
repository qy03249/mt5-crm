"""add crm user mt5 fields

Revision ID: 20260613_0005
Revises: 20260613_0004
Create Date: 2026-06-13 22:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260613_0005"
down_revision: str | None = "20260613_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 为 CRM 用户列表补充 MT5 账号展示字段，对应页面“MT5账号”和“上级MT5账号”列。
    op.add_column(
        "crm_users",
        sa.Column("mt5_login", sa.String(length=64), nullable=True, comment="MT5账号"),
    )
    op.add_column(
        "crm_users",
        sa.Column(
            "parent_mt5_login",
            sa.String(length=64),
            nullable=True,
            comment="上级MT5账号",
        ),
    )
    op.create_index("ix_crm_users_mt5_login", "crm_users", ["mt5_login"])

    # 更新本地演示数据，方便页面筛选和导出时验证 MT5 账号字段。
    op.execute(
        """
        UPDATE crm_users
        SET mt5_login = '800001'
        WHERE username = 'agent001'
        """
    )
    op.execute(
        """
        UPDATE crm_users
        SET mt5_login = '900001', parent_mt5_login = '800001'
        WHERE username = 'client001'
        """
    )


def downgrade() -> None:
    # 回滚 MT5 展示字段。
    op.drop_index("ix_crm_users_mt5_login", table_name="crm_users")
    op.drop_column("crm_users", "parent_mt5_login")
    op.drop_column("crm_users", "mt5_login")
