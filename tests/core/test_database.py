from app.core.config import Settings
from app.core.database import build_engine


def test_build_engine_uses_settings_database_url():
    settings = Settings(
        mysql_host="127.0.0.1",
        mysql_port=3306,
        mysql_user="root",
        mysql_password="root",
        mysql_database="mt5_crm_test",
    )

    engine = build_engine(settings)

    assert str(engine.url) == "mysql+pymysql://root:***@127.0.0.1:3306/mt5_crm_test?charset=utf8mb4"
