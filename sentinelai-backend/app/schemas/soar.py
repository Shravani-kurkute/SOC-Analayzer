from datetime import datetime
from typing import Any

from pydantic import Field
from app.schemas.base import BaseSchema


class PlaybookCreate(BaseSchema):
    name: str
    description: str | None = None
    playbook_type: str
    severity: str = "medium"
    category: str | None = None
    tags: list[str] | None = None
    is_template: bool = False
    steps: list[dict[str, Any]] = []
    config: dict[str, Any] | None = None


class PlaybookUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    playbook_type: str | None = None
    severity: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_active: bool | None = None
    is_template: bool | None = None
    steps: list[dict[str, Any]] | None = None
    config: dict[str, Any] | None = None


class PlaybookResponse(BaseSchema):
    id: str
    name: str
    description: str | None = None
    playbook_type: str
    severity: str
    category: str | None = None
    tags: list[str] | None = None
    is_template: bool = False
    is_active: bool = True
    steps: list[dict[str, Any]] | None = None
    config: dict[str, Any] | None = None
    execution_count: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 0.0
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None


class PlaybookListItem(BaseSchema):
    id: str
    name: str
    playbook_type: str
    severity: str
    category: str | None = None
    is_template: bool = False
    is_active: bool = True
    execution_count: int = 0
    success_rate: float = 0.0
    created_at: datetime


class PlaybookExecutionCreate(BaseSchema):
    playbook_id: str
    incident_id: str | None = None
    triggered_by: str | None = None


class PlaybookExecutionResponse(BaseSchema):
    id: str
    playbook_id: str
    playbook_name: str
    incident_id: str | None = None
    status: str
    current_step: int = 0
    total_steps: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    triggered_by: str | None = None
    error_message: str | None = None
    failed_step: int | None = None
    execution_data: dict[str, Any] | None = None
    ai_summary: str | None = None
    created_at: datetime


class PlaybookExecutionLogResponse(BaseSchema):
    id: str
    execution_id: str
    step_index: int
    step_name: str
    action_type: str
    status: str
    message: str | None = None
    duration_ms: int | None = None
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime


class ApprovalRequestCreate(BaseSchema):
    execution_id: str
    step_index: int
    action_type: str
    reason: str | None = None


class ApprovalRequestResponse(BaseSchema):
    id: str
    playbook_id: str
    execution_id: str
    incident_id: str | None = None
    step_index: int
    action_type: str
    requested_by: str | None = None
    approved_by: str | None = None
    status: str
    reason: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class ApprovalAction(BaseSchema):
    approve: bool = True
    reason: str | None = None


class PlaybookStats(BaseSchema):
    total_playbooks: int = 0
    active_playbooks: int = 0
    executions_today: int = 0
    total_executions: int = 0
    success_rate: float = 0.0
    avg_execution_time_ms: float = 0.0
    pending_approvals: int = 0
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    recent_executions: list[dict[str, Any]] = []


class ExecuteResponse(BaseSchema):
    execution_id: str
    status: str
    message: str
