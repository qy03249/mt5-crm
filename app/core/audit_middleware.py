import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.types import Message

from app.core.audit import build_operation_log_params, dump_params_json
from app.core.database import SessionLocal
from app.modules.admin.models import OperationLog

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def replay_request_body(request: Request, body: bytes) -> None:
    async def receive() -> Message:
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive


def parse_json_body(body: bytes) -> Any:
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return {"raw": body.decode("utf-8", errors="replace")}


def should_audit_request(request: Request) -> bool:
    return request.method in WRITE_METHODS and request.url.path.startswith("/api/v1/")


def get_audit_session(request: Request) -> Session:
    if hasattr(request.app.state, "audit_session_factory"):
        return request.app.state.audit_session_factory()
    return SessionLocal()


async def audit_operation_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if not should_audit_request(request):
        return await call_next(request)

    body = await request.body()
    await replay_request_body(request, body)
    response = await call_next(request)

    params = build_operation_log_params(
        query_params=request.query_params,
        body=parse_json_body(body),
    )
    client_host = request.client.host if request.client else ""
    log = OperationLog(
        operator_id=None,
        operator_name="anonymous",
        path=request.url.path,
        method=request.method,
        ip_address=client_host,
        user_agent=request.headers.get("user-agent"),
        params_json=dump_params_json(params),
        result="success" if response.status_code < 400 else "failure",
    )

    with get_audit_session(request) as db:
        db.add(log)
        db.commit()

    return response
