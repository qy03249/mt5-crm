from pathlib import Path

from alembic.config import Config


def test_alembic_points_to_migrations_directory():
    config = Config("alembic.ini")

    assert config.get_main_option("script_location") == "migrations"
    assert Path("migrations/env.py").is_file()
