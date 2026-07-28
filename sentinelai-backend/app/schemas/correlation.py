from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema


class CorrelationEventSchema(BaseSchema):
    id: str
    group_id: str
    parsed_event_id: str | None = None
    log_entry_id: str | None = None
    event_type: str
    event_source: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    timestamp: datetime
    action: str | None = None
    severity: str | None = None
    risk_score: float | None = None
    raw_message: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime


class CorrelationGroupSchema(BaseSchema):
    id: str
    correlation_id: str
    group_type: str
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    hostname: str | None = None
    session_id: str | None = None
    start_time: datetime
    end_time: datetime
    event_count: int
    risk_score: float
    status: str
    attack_chain: list[str] | None = None
    metadata: dict[str, Any] | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    events: list[CorrelationEventSchema] = []


class CorrelationGroupListSchema(BaseSchema):
    id: str
    correlation_id: str
    group_type: str
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    hostname: str | None = None
    start_time: datetime
    end_time: datetime
    event_count: int
    risk_score: float
    status: str
    attack_chain: list[str] | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class CorrelationStats(BaseSchema):
    total_groups: int
    open_groups: int
    avg_risk_score: float
    total_events_correlated: int
    groups_by_type: dict[str, int]
    groups_by_status: dict[str, int]


class CorrelationRunResult(BaseSchema):
    groups_created: int
    events_correlated: int
    message: str
