from app.core.config import Settings


def test_settings_have_expected_service_defaults():
    settings = Settings()

    assert settings.app_name == "MT5 CRM API"
    assert settings.api_v1_prefix == "/api/v1"


def test_settings_build_mysql_database_url_from_components():
    settings = Settings(
        mysql_host="db.example.test",
        mysql_port=3307,
        mysql_user="crm_user",
        mysql_password="secret",
        mysql_database="mt5_crm_test",
    )

    assert (
        settings.database_url
        == "mysql+pymysql://crm_user:secret@db.example.test:3307/mt5_crm_test?charset=utf8mb4"
    )
