from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema


class AlertResponse(BaseSchema):
    id: str
    title: str
    description: str | None = None
    severity: str
    status: str
    source: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: int | None = None
    destination_port: int | None = None
    protocol: str | None = None
    mitre_technique_id: str | None = None
    mitre_tactic: str | None = None
    rule_id: str | None = None
    rule_name: str | None = None
    score: int = 0
    raw_data: dict[str, Any] | None = None
    enriched_data: dict[str, Any] | None = None
    tags: list[str] | None = None
    asset_ids: list[str] | None = None
    country: str | None = None
    city: str | None = None
    correlation_group_id: str | None = None
    recommendation: str | None = None
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    incident_id: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None


class AlertUpdate(BaseSchema):
    status: str | None = None
    acknowledged_by: str | None = None
    resolved_by: str | None = None
    incident_id: str | None = None


class AlertStatsResponse(BaseSchema):
    total: int
    by_severity: dict[str, int]
    by_status: dict[str, int]
    by_rule: dict[str, int]
    top_source_ips: list[dict[str, Any]]
    avg_score: float
    recent_trend: list[dict[str, Any]]


class AlertListResponse(BaseSchema):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
