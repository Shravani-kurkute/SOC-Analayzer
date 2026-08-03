from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema


class AIInvestigationResponse(BaseSchema):
    id: str
    incident_id: str
    provider: str
    summary: str | None = None
    attack_explanation: str | None = None
    timeline_data: list[dict[str, Any]] | None = None
    root_cause: str | None = None
    mitre_explanation: str | None = None
    ioc_summary: str | None = None
    risk_explanation: str | None = None
    recommendations: list[dict[str, Any]] | None = None
    containment: str | None = None
    recovery: str | None = None
    hunting_queries: list[dict[str, Any]] | None = None
    false_positive_probability: float | None = None
    confidence_score: float | None = None
    tokens_used: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: datetime
    prompt: str | None = None


class AIInvestigationListItem(BaseSchema):
    id: str
    incident_id: str
    incident_title: str | None = None
    provider: str
    summary: str | None = None
    confidence_score: float | None = None
    tokens_used: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: datetime


class AIInvestigateRequest(BaseSchema):
    provider: str | None = None


class AIInvestigationStats(BaseSchema):
    total_investigations: int = 0
    average_confidence: float = 0.0
    average_latency_ms: float = 0.0
    provider_usage: dict[str, int] = {}
    recent_investigations: list[AIInvestigationListItem] = []
