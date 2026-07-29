from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class MitreTechnique(BaseModel):
    __tablename__ = "mitre_techniques"

    technique_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tactic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tactic_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    platform: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    permissions_required: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    detection: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_subtechnique: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_technique_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    mitre_version: Mapped[str] = mapped_column(String(10), default="15.1", nullable=False)
    detection_rules: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    ioc_indicators: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    kill_chain_phase: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_sources: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class MitreMapping(BaseModel):
    __tablename__ = "mitre_mappings"

    technique_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    mapped_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mapped_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mapped_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="auto", nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    mapped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)


class CoverageStatistic(BaseModel):
    __tablename__ = "coverage_statistics"

    tactic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    total_techniques: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mapped_techniques: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coverage_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_detections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mapped_detections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
