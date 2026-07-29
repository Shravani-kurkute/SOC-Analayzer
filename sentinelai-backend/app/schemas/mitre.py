from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema


class MitreTechniqueResponse(BaseSchema):
    id: str
    technique_id: str
    name: str
    description: str | None = None
    tactic: str
    tactic_id: str | None = None
    platform: list[str] | None = None
    permissions_required: list[str] | None = None
    detection: str | None = None
    is_subtechnique: bool = False
    parent_technique_id: str | None = None
    severity: str = "medium"
    score: float = 1.0
    mitre_version: str = "15.1"
    detection_rules: list[str] | None = None
    ioc_indicators: list[str] | None = None
    kill_chain_phase: str | None = None
    data_sources: list[str] | None = None
    url: str | None = None
    created_at: datetime
    updated_at: datetime


class MitreMappingResponse(BaseSchema):
    id: str
    technique_id: str
    mapped_type: str
    mapped_id: str
    mapped_name: str | None = None
    confidence: float
    source: str
    context: str | None = None
    mapped_at: datetime
    extra_data: dict[str, Any] | None = Field(None, validation_alias="metadata")
    created_at: datetime


class CoverageStatisticResponse(BaseSchema):
    tactic: str
    total_techniques: int
    mapped_techniques: int
    coverage_percent: float
    total_detections: int
    mapped_detections: int
    avg_confidence: float
    calculated_at: datetime


class MitreCoverageResponse(BaseSchema):
    overall_coverage: float
    total_techniques: int
    total_mapped: int
    total_detections: int
    by_tactic: list[CoverageStatisticResponse]
    top_techniques: list[dict[str, Any]]
    top_tactics: list[dict[str, Any]]
    most_triggered: list[dict[str, Any]]


class MitreMapRequest(BaseSchema):
    mapped_type: str
    mapped_id: str
    mapped_name: str | None = None
    context: str | None = None


class MitreMapResponse(BaseSchema):
    mappings: list[MitreMappingResponse]
    new_mappings: int
    confidence_avg: float


class MitreTechniqueDetail(BaseSchema):
    technique: MitreTechniqueResponse
    mappings: list[MitreMappingResponse]
    mapped_count: int
    detection_coverage: float
    related_techniques: list[MitreTechniqueResponse]
