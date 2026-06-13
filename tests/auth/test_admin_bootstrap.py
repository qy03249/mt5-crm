from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.admin.bootstrap import ensure_initial_admin
from app.modules.admin.models import AdminUser, Permission, Role
from app.modules.auth.security import verify_password


def test_ensure_initial_admin_creates_admin_role_permissions_and_account():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        admin = ensure_initial_admin(
            session,
            username="admin",
            password="Admin@123456",
            email="admin@example.test",
        )
        admin_again = ensure_initial_admin(
            session,
            username="admin",
            password="Changed@123456",
            email="changed@example.test",
        )

        assert admin.id == admin_again.id
        assert session.query(AdminUser).count() == 1
        assert session.query(Role).count() == 1
        assert session.query(Permission).count() >= 6
        assert admin.username == "admin"
        assert admin.email == "admin@example.test"
        assert verify_password("Admin@123456", admin.password_hash)
        assert {role.code for role in admin.roles} == {"admin"}

        setting = session.query(Permission).filter_by(code="setting.view").one()
        backend_permission = session.query(Permission).filter_by(
            code="setting.backend_permission.view"
        ).one()
        account_menu = session.query(Permission).filter_by(code="admin.account.view").one()
        role_menu = session.query(Permission).filter_by(code="admin.role.view").one()
        account_manage = session.query(Permission).filter_by(
            code="admin.account.manage"
        ).one()
        role_manage = session.query(Permission).filter_by(code="admin.role.manage").one()

        assert backend_permission.parent_id == setting.id
        assert account_menu.parent_id == backend_permission.id
        assert role_menu.parent_id == backend_permission.id
        assert account_manage.parent_id == account_menu.id
        assert role_manage.parent_id == role_menu.id
