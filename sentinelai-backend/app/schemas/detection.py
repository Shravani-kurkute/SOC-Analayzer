from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DetectionEvent(BaseModel):
    id: str | None = None
    source: str | None = None
    action: str | None = None
    username: str | None = None
    src_ip: str | None = None
    dest_ip: str | None = None
    src_port: int | None = None
    dest_port: int | None = None
    protocol: str | None = None
    log_source: str | None = None
    timestamp: str | None = None
    raw: dict[str, Any] | None = None
    country: str | None = None
    city: str | None = None
    asset_id: str | None = None

    class Config:
        extra = "allow"
        from_attributes = True


class DetectionResult:
    def __init__(
        self,
        title: str,
        description: str | None = None,
        severity: str = "medium",
        source: str | None = None,
        source_ip: str | None = None,
        destination_ip: str | None = None,
        source_port: int | None = None,
        destination_port: int | None = None,
        protocol: str | None = None,
        mitre_technique_id: str | None = None,
        mitre_tactic: str | None = None,
        rule_id: str | None = None,
        rule_name: str | None = None,
        score: int = 0,
        raw_data: dict[str, Any] | None = None,
        enriched_data: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        asset_ids: list[str] | None = None,
        country: str | None = None,
        city: str | None = None,
        correlation_group_id: str | None = None,
        recommendation: str | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.severity = severity
        self.source = source
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.source_port = source_port
        self.destination_port = destination_port
        self.protocol = protocol
        self.mitre_technique_id = mitre_technique_id
        self.mitre_tactic = mitre_tactic
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.score = score
        self.raw_data = raw_data
        self.enriched_data = enriched_data
        self.tags = tags or []
        self.asset_ids = asset_ids or []
        self.country = country
        self.city = city
        self.correlation_group_id = correlation_group_id
        self.recommendation = recommendation


class DetectionRunRequest(BaseModel):
    event_ids: list[str] | None = None
    rule_ids: list[str] | None = None


class DetectionRunResponse(BaseModel):
    alerts_created: int
    alerts: list[dict[str, Any]] = []


class DetectionStatusResponse(BaseModel):
    engine_version: str = "1.0.0"
    total_rules: int = 0
    enabled_rules: int = 0
    modules_loaded: list[str] = []
