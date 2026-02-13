from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    trigger_key: str = Field(pattern=r'^[a-zA-Z0-9_-]{6,128}$')
    action_url: HttpUrl
    action_method: Literal['POST', 'PUT', 'PATCH'] = 'POST'
    action_headers: dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=10, ge=1, le=30)


class WorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    trigger_key: str
    action_url: str
    action_method: str
    action_headers: dict[str, str]
    timeout_seconds: int
    created_at: datetime


class TriggerAccepted(BaseModel):
    run_id: int
    status: str


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    status: str
    idempotency_key: str
    trigger_payload: dict[str, Any]
    error_message: str | None
    created_at: datetime
    updated_at: datetime
