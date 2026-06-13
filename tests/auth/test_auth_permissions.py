import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.modules.admin.models import AdminUser, OperationLog, Permission, Role
from app.modules.auth.security import hash_password


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.state.audit_session_factory = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        del app.state.audit_session_factory


def seed_admin_with_menu_permission(db: Session) -> AdminUser:
    role = Role(code="admin", name="管理员")
    setting_permission = Permission(
        code="setting.view",
        name="设置",
        type="menu",
        path="/setting",
    )
    backend_permission = Permission(
        code="setting.backend_permission.view",
        name="后台权限",
        type="menu",
        path=None,
        parent_id=1,
    )
    account_menu = Permission(
        code="admin.account.view",
        name="后台账户",
        type="menu",
        path="/setting/permissions/account",
        parent_id=2,
    )
    permission = Permission(
        code="dashboard.view",
        name="首页",
        type="menu",
        path="/home",
    )
    button_permission = Permission(
        code="admin.account.manage",
        name="后台账户管理",
        type="button",
        path="/setting/permissions/account",
        parent_id=3,
    )
    admin = AdminUser(
        username="admin",
        password_hash=hash_password("Admin@123456"),
        display_name="系统管理员",
        email="admin@example.test",
        status="active",
    )
    role.permissions.extend(
        [
            setting_permission,
            backend_permission,
            account_menu,
            permission,
            button_permission,
        ]
    )
    admin.roles.append(role)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def login(client: TestClient, username: str = "admin", password: str = "Admin@123456") -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_login_and_read_current_user(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    token = login(client)
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me.status_code == 200
    assert me.json() == {
        "id": 1,
        "username": "admin",
        "display_name": "系统管理员",
        "email": "admin@example.test",
        "roles": [{"id": 1, "code": "admin", "name": "管理员"}],
    }


def test_login_rejects_wrong_password(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": "http_error",
        "message": "Invalid username or password",
        "data": None,
    }


def test_protected_api_requires_unified_auth_error(client: TestClient):
    response = client.get("/api/v1/admin/accounts")

    assert response.status_code == 401
    assert response.json() == {
        "code": "http_error",
        "message": "Not authenticated",
        "data": None,
    }


def test_validation_error_uses_unified_response(client: TestClient):
    response = client.post("/api/v1/auth/login", json={"username": "admin"})

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["message"] == "请求参数校验失败"
    assert response.json()["data"][0]["loc"] == ["body", "password"]


def test_write_api_creates_operation_log(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123456"},
    )

    assert response.status_code == 200
    log = db_session.query(OperationLog).one()
    assert log.operator_name == "anonymous"
    assert log.path == "/api/v1/auth/login"
    assert log.method == "POST"
    assert log.result == "success"
    assert '"password": "***"' in log.params_json


def test_admin_can_read_operation_logs(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)
    token = login(client)

    response = client.get(
        "/api/v1/admin/operation-logs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()[0]["path"] == "/api/v1/auth/login"
    assert response.json()[0]["method"] == "POST"
    assert response.json()[0]["result"] == "success"
    assert response.json()[0]["params_json"]["body"]["password"] == "***"


def test_current_user_can_read_menu_permissions(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    token = login(client)
    response = client.get(
        "/api/v1/admin/permissions/menus",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "code": "setting.view",
            "name": "设置",
            "type": "menu",
            "path": "/setting",
            "parent_id": None,
        },
        {
            "id": 2,
            "code": "setting.backend_permission.view",
            "name": "后台权限",
            "type": "menu",
            "path": None,
            "parent_id": 1,
        },
        {
            "id": 3,
            "code": "admin.account.view",
            "name": "后台账户",
            "type": "menu",
            "path": "/setting/permissions/account",
            "parent_id": 2,
        },
        {
            "id": 4,
            "code": "dashboard.view",
            "name": "首页",
            "type": "menu",
            "path": "/home",
            "parent_id": None,
        }
    ]


def test_current_user_can_read_button_permissions(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    token = login(client)
    response = client.get(
        "/api/v1/admin/permissions/buttons",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5,
            "code": "admin.account.manage",
            "name": "后台账户管理",
            "type": "button",
            "path": "/setting/permissions/account",
            "parent_id": 3,
        }
    ]


def test_admin_can_read_permission_tree(client: TestClient, db_session: Session):
    seed_admin_with_menu_permission(db_session)

    token = login(client)
    response = client.get(
        "/api/v1/admin/permissions/tree",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()[0] == {
        "id": 1,
        "code": "setting.view",
        "name": "设置",
        "type": "menu",
        "path": "/setting",
        "parent_id": None,
        "children": [
            {
                "id": 2,
                "code": "setting.backend_permission.view",
                "name": "后台权限",
                "type": "menu",
                "path": None,
                "parent_id": 1,
                "children": [
                    {
                        "id": 3,
                        "code": "admin.account.view",
                        "name": "后台账户",
                        "type": "menu",
                        "path": "/setting/permissions/account",
                        "parent_id": 2,
                        "children": [
                            {
                                "id": 5,
                                "code": "admin.account.manage",
                                "name": "后台账户管理",
                                "type": "button",
                                "path": "/setting/permissions/account",
                                "parent_id": 3,
                                "children": [],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_admin_can_create_role_permission_account_and_assign_permission(
    client: TestClient, db_session: Session
):
    seed_admin_with_menu_permission(db_session)
    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}

    role = client.post(
        "/api/v1/admin/roles",
        json={"code": "finance", "name": "财务"},
        headers=headers,
    )
    permission = client.post(
        "/api/v1/admin/permissions",
        json={
            "code": "finance.deposit.review",
            "name": "入金审核",
            "type": "button",
            "path": "/task/deposit",
        },
        headers=headers,
    )
    assign = client.put(
        f"/api/v1/admin/roles/{role.json()['id']}/permissions",
        json={"permission_ids": [permission.json()["id"]]},
        headers=headers,
    )
    account = client.post(
        "/api/v1/admin/accounts",
        json={
            "username": "finance01",
            "password": "Finance@123456",
            "display_name": "财务一号",
            "email": "finance01@example.test",
            "role_ids": [role.json()["id"]],
        },
        headers=headers,
    )

    assert role.status_code == 201
    assert permission.status_code == 201
    assert assign.status_code == 200
    assert assign.json()["permission_count"] == 1
    assert account.status_code == 201
    assert account.json()["username"] == "finance01"
