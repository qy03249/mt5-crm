import json
from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = {"password", "password_hash", "token", "access_token", "refresh_token", "secret"}


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in SENSITIVE_KEYS:
                redacted[key_text] = "***"
            else:
                redacted[key_text] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def build_operation_log_params(
    *,
    query_params: Mapping[str, Any],
    body: Any,
) -> dict[str, Any]:
    return {
        "query": dict(query_params),
        "body": redact_sensitive(body),
    }


def dump_params_json(params: dict[str, Any]) -> str:
    return json.dumps(params, ensure_ascii=False, default=str)
