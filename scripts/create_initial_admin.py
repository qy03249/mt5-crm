import sys
from pathlib import Path

# 允许直接运行本脚本：python scripts/create_initial_admin.py
# 直接运行时 sys.path 默认指向 scripts 目录，需要手动加入项目根目录。
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.modules.admin.bootstrap import ensure_initial_admin  # noqa: E402


def main() -> None:
    with SessionLocal() as db:
        admin = ensure_initial_admin(
            db,
            username=settings.initial_admin_username,
            password=settings.initial_admin_password,
            email=settings.initial_admin_email,
        )
        print(f"Initial admin ready: {admin.username}")


if __name__ == "__main__":
    main()
