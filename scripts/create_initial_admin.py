from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.admin.bootstrap import ensure_initial_admin


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
