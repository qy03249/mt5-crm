"""seed permission tree

Revision ID: 20260613_0002
Revises: 20260613_0001
Create Date: 2026-06-13 21:10:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260613_0002"
down_revision: str | None = "20260613_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 创建“设置 > 后台权限”目录，匹配参考系统左侧设置菜单分组。
    op.execute(
        """
        INSERT INTO permissions (
            `code`, `name`, `type`, `path`, `parent_id`, `created_at`, `updated_at`
        )
        SELECT
            'setting.backend_permission.view',
            '后台权限',
            'menu',
            NULL,
            setting_permission.id,
            NOW(),
            NOW()
        FROM permissions AS setting_permission
        WHERE setting_permission.`code` = 'setting.view'
          AND NOT EXISTS (
              SELECT 1 FROM permissions AS existing_permission
              WHERE existing_permission.`code` = 'setting.backend_permission.view'
          )
        """
    )

    # 创建“后台账户”菜单，作为后台权限目录下的子菜单。
    op.execute(
        """
        INSERT INTO permissions (
            `code`, `name`, `type`, `path`, `parent_id`, `created_at`, `updated_at`
        )
        SELECT
            'admin.account.view',
            '后台账户',
            'menu',
            '/setting/permissions/account',
            backend_permission.id,
            NOW(),
            NOW()
        FROM permissions AS backend_permission
        WHERE backend_permission.`code` = 'setting.backend_permission.view'
          AND NOT EXISTS (
              SELECT 1 FROM permissions AS existing_permission
              WHERE existing_permission.`code` = 'admin.account.view'
          )
        """
    )

    # 创建“角色权限”菜单，作为后台权限目录下的子菜单。
    op.execute(
        """
        INSERT INTO permissions (
            `code`, `name`, `type`, `path`, `parent_id`, `created_at`, `updated_at`
        )
        SELECT
            'admin.role.view',
            '角色权限',
            'menu',
            '/setting/permissions/role',
            backend_permission.id,
            NOW(),
            NOW()
        FROM permissions AS backend_permission
        WHERE backend_permission.`code` = 'setting.backend_permission.view'
          AND NOT EXISTS (
              SELECT 1 FROM permissions AS existing_permission
              WHERE existing_permission.`code` = 'admin.role.view'
          )
        """
    )

    # 修正旧按钮权限的父级，按钮挂到具体页面菜单下，菜单树不再平铺。
    op.execute(
        """
        UPDATE permissions AS permission
        JOIN permissions AS account_menu
            ON account_menu.`code` = 'admin.account.view'
        SET
            permission.`name` = '后台账户管理',
            permission.`type` = 'button',
            permission.`path` = '/setting/permissions/account',
            permission.`parent_id` = account_menu.id,
            permission.`updated_at` = NOW()
        WHERE permission.`code` = 'admin.account.manage'
        """
    )
    op.execute(
        """
        UPDATE permissions AS permission
        JOIN permissions AS role_menu
            ON role_menu.`code` = 'admin.role.view'
        SET
            permission.`name` = '角色权限管理',
            permission.`type` = 'button',
            permission.`path` = '/setting/permissions/role',
            permission.`parent_id` = role_menu.id,
            permission.`updated_at` = NOW()
        WHERE permission.`code` = 'admin.role.manage'
        """
    )

    # 确保超级管理员拥有新增的后台权限目录和两个子菜单。
    op.execute(
        """
        INSERT INTO role_permissions (`role_id`, `permission_id`)
        SELECT admin_role.id, permission.id
        FROM roles AS admin_role
        JOIN permissions AS permission
            ON permission.`code` IN (
                'setting.backend_permission.view',
                'admin.account.view',
                'admin.role.view'
            )
        WHERE admin_role.`code` = 'admin'
          AND NOT EXISTS (
              SELECT 1
              FROM role_permissions AS existing_relation
              WHERE existing_relation.`role_id` = admin_role.id
                AND existing_relation.`permission_id` = permission.id
          )
        """
    )


def downgrade() -> None:
    # 回滚时移除本迁移新增的菜单权限，并保留原有后台账号和角色按钮权限。
    op.execute(
        """
        DELETE role_permission
        FROM role_permissions AS role_permission
        JOIN permissions AS permission
            ON permission.id = role_permission.`permission_id`
        WHERE permission.`code` IN (
            'setting.backend_permission.view',
            'admin.account.view',
            'admin.role.view'
        )
        """
    )
    op.execute(
        """
        UPDATE permissions
        SET `parent_id` = NULL, `updated_at` = NOW()
        WHERE `code` IN ('admin.account.manage', 'admin.role.manage')
        """
    )
    op.execute(
        """
        DELETE FROM permissions
        WHERE `code` IN (
            'admin.account.view',
            'admin.role.view',
            'setting.backend_permission.view'
        )
        """
    )
