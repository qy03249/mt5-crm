from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router

app = FastAPI(title="MT5 CRM API")

STATIC_DIR = Path(__file__).resolve().parent / "static"

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "mt5-crm-api"}


@app.get("/")
def frontend_app() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
