from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_status():
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "mt5-crm-api"}


def test_root_serves_frontend_app():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "MT5 CRM" in response.text


def test_frontend_static_script_contains_reference_menu_skeleton():
    client = TestClient(app)

    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "认证审核" in response.text
    assert "CRM用户" in response.text
    assert "入金报表" in response.text
    assert "后台权限" in response.text
