"""create operation logs

Revision ID: 20260613_0003
Revises: 20260613_0002
Create Date: 2026-06-13 21:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260613_0003"
down_revision: str | None = "20260613_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 创建后台操作日志表，用于记录后台写操作审计轨迹。
    op.create_table(
        "operation_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("operator_id", sa.Integer(), nullable=True, comment="操作员后台账号ID"),
        sa.Column("operator_name", sa.String(length=64), nullable=False, comment="操作员名称"),
        sa.Column("path", sa.String(length=255), nullable=False, comment="请求路径"),
        sa.Column("method", sa.String(length=16), nullable=False, comment="HTTP请求方法"),
        sa.Column("ip_address", sa.String(length=64), nullable=False, comment="客户端IP地址"),
        sa.Column(
            "user_agent",
            sa.String(length=512),
            nullable=True,
            comment="浏览器或客户端信息",
        ),
        sa.Column(
            "params_json",
            sa.Text(),
            nullable=True,
            comment="请求参数JSON，敏感字段已脱敏",
        ),
        sa.Column(
            "result",
            sa.String(length=32),
            nullable=False,
            comment="操作结果：success/failure",
        ),
        sa.Column("operated_at", sa.DateTime(), nullable=False, comment="操作时间"),
        sa.PrimaryKeyConstraint("id"),
        comment="后台操作日志表",
    )
    op.create_index("ix_operation_logs_operated_at", "operation_logs", ["operated_at"])
    op.create_index("ix_operation_logs_operator_id", "operation_logs", ["operator_id"])


def downgrade() -> None:
    # 回滚时删除后台操作日志表及索引。
    op.drop_index("ix_operation_logs_operator_id", table_name="operation_logs")
    op.drop_index("ix_operation_logs_operated_at", table_name="operation_logs")
    op.drop_table("operation_logs")
