import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.modules.admin.models import AdminUser, Role
from app.modules.auth.security import create_access_token, hash_password
from app.modules.crm.models import CrmUser


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


def seed_admin(db: Session) -> AdminUser:
    role = Role(code="admin", name="管理员")
    admin = AdminUser(
        username="admin",
        password_hash=hash_password("Admin@123456"),
        display_name="系统管理员",
        email="admin@example.test",
        status="active",
    )
    admin.roles.append(role)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def auth_headers(admin: AdminUser) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(admin.id))}"}


def test_admin_can_list_crm_users(client: TestClient, db_session: Session):
    admin = seed_admin(db_session)
    parent = CrmUser(
        username="agent001",
        name="上级代理",
        email="agent@example.test",
        phone="13800000000",
        parent_code="AG001",
        role_type="agent",
        certification_status="approved",
        status="active",
        remark="测试代理",
    )
    user = CrmUser(
        username="client001",
        name="张三",
        nickname="客户一号",
        email="client@example.test",
        phone="13900000000",
        parent=parent,
        parent_code="AG001",
        role_type="customer",
        certification_status="pending",
        status="active",
        remark="首个CRM客户",
    )
    db_session.add_all([parent, user])
    db_session.commit()

    response = client.get("/api/v1/crm/users", headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json()[0]["username"] == "client001"
    assert response.json()[0]["name"] == "张三"
    assert response.json()[0]["parent_name"] == "上级代理"
    assert response.json()[0]["remark"] == "首个CRM客户"


def test_admin_can_create_crm_user(client: TestClient, db_session: Session):
    admin = seed_admin(db_session)
    parent = CrmUser(
        username="agent001",
        name="上级代理",
        email="agent@example.test",
        parent_code="AG001",
        role_type="agent",
        certification_status="approved",
        status="active",
    )
    db_session.add(parent)
    db_session.commit()

    response = client.post(
        "/api/v1/crm/users",
        headers=auth_headers(admin),
        json={
            "username": "client002",
            "name": "李四",
            "nickname": "客户二号",
            "phone": "13700000000",
            "email": "client2@example.test",
            "parent_id": parent.id,
            "parent_code": "AG001",
            "role_type": "customer",
            "certification_status": "pending",
            "remark": "页面新增客户",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "client002"
    assert response.json()["name"] == "李四"
    assert response.json()["parent_name"] == "上级代理"
    assert response.json()["status"] == "active"


def test_admin_can_read_update_and_change_crm_user_status(
    client: TestClient,
    db_session: Session,
):
    admin = seed_admin(db_session)
    user = CrmUser(
        username="client003",
        name="王五",
        phone="13600000000",
        email="client3@example.test",
        role_type="customer",
        certification_status="pending",
        status="active",
        remark="待编辑客户",
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id
    headers = auth_headers(admin)

    detail = client.get(f"/api/v1/crm/users/{user_id}", headers=headers)
    update = client.put(
        f"/api/v1/crm/users/{user_id}",
        headers=headers,
        json={
            "username": "client003",
            "name": "王五编辑",
            "nickname": "编辑昵称",
            "phone": "13611111111",
            "email": "client3-edit@example.test",
            "parent_id": None,
            "parent_code": None,
            "role_type": "ib",
            "certification_status": "approved",
            "status": "active",
            "remark": "已编辑客户",
        },
    )
    status_response = client.patch(
        f"/api/v1/crm/users/{user_id}/status",
        headers=headers,
        json={"status": "disabled"},
    )

    assert detail.status_code == 200
    assert detail.json()["name"] == "王五"
    assert update.status_code == 200
    assert update.json()["name"] == "王五编辑"
    assert update.json()["role_type"] == "ib"
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "disabled"
