from __future__ import annotations

from typing import Any

import httpx


class ExecutionError(Exception):
    pass


def execute_webhook_action(
    *, action_url: str, action_method: str, action_headers: dict[str, Any], payload: dict[str, Any], timeout_seconds: int
) -> int:
    method = action_method.upper()
    if method not in {'POST', 'PUT', 'PATCH'}:
        raise ExecutionError(f'unsupported action_method: {method}')

    headers = {str(k): str(v) for k, v in action_headers.items()}
    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.request(method=method, url=action_url, headers=headers, json=payload)

    if 200 <= response.status_code < 300:
        return response.status_code
    if 500 <= response.status_code < 600:
        raise ExecutionError(f'transient downstream status={response.status_code}')
    raise ExecutionError(f'non-retryable downstream status={response.status_code}')
