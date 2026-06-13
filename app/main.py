from fastapi import FastAPI

app = FastAPI(title="MT5 CRM API")


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "mt5-crm-api"}
