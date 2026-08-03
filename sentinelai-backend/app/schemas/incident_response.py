from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema


class IncidentCommentResponse(BaseSchema):
    id: str
    incident_id: str
    author_id: str | None = None
    author_name: str
    content: str
    is_edited: bool = False
    created_at: datetime
    updated_at: datetime


class IncidentCommentCreate(BaseSchema):
    content: str


class IncidentCommentUpdate(BaseSchema):
    content: str


class IncidentTaskResponse(BaseSchema):
    id: str
    incident_id: str
    title: str
    description: str | None = None
    status: str = "pending"
    priority: str = "medium"
    assignee_id: str | None = None
    assignee_name: str | None = None
    due_date: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IncidentTaskCreate(BaseSchema):
    title: str
    description: str | None = None
    priority: str = "medium"
    assignee_id: str | None = None
    due_date: datetime | None = None


class IncidentTaskUpdate(BaseSchema):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None


class IncidentEvidenceResponse(BaseSchema):
    id: str
    incident_id: str
    filename: str
    file_type: str
    file_size: int
    sha256: str
    uploaded_by: str
    description: str | None = None
    created_at: datetime


class IncidentEvidenceCreate(BaseSchema):
    description: str | None = None


class IncidentTimelineResponse(BaseSchema):
    id: str
    incident_id: str
    action: str
    actor: str
    details: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime


class IncidentDetailResponse(BaseSchema):
    id: str
    title: str
    description: str | None = None
    severity: str
    status: str
    category: str | None = None
    alert_ids: list[str] | None = None
    asset_ids: list[str] | None = None
    assignee_id: str | None = None
    assignee_name: str | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    comments: list[IncidentCommentResponse] = []
    tasks: list[IncidentTaskResponse] = []
    evidence: list[IncidentEvidenceResponse] = []
    timeline: list[IncidentTimelineResponse] = []


class IncidentListItem(BaseSchema):
    id: str
    title: str
    severity: str
    status: str
    category: str | None = None
    assignee_id: str | None = None
    assignee_name: str | None = None
    alert_count: int = 0
    task_count: int = 0
    task_done: int = 0
    evidence_count: int = 0
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None


class IncidentCreate(BaseSchema):
    title: str
    description: str | None = None
    severity: str = "medium"
    category: str | None = None
    alert_ids: list[str] | None = None
    asset_ids: list[str] | None = None


class IncidentUpdate(BaseSchema):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    category: str | None = None
    alert_ids: list[str] | None = None
    asset_ids: list[str] | None = None


class IncidentAssign(BaseSchema):
    user_id: str


class IncidentClose(BaseSchema):
    resolution: str | None = None
    notes: str | None = None
