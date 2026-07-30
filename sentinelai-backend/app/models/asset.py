from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class Asset(BaseModel):
    __tablename__ = "assets"

    hostname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    os: Mapped[str | None] = mapped_column(String(100), nullable=True)
    os_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(30), default="server", nullable=False)
    criticality: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    environment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    vulnerability_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_ports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discovery_source: Mapped[str | None] = mapped_column(String(50), nullable=True)


class AssetRisk(BaseModel):
    __tablename__ = "asset_risks"

    asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    open_incidents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_alerts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    threat_intel_matches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exposure_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    criticality_weight: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AssetOwner(BaseModel):
    __tablename__ = "asset_owners"

    asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AssetGroup(BaseModel):
    __tablename__ = "asset_groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)


class AssetTag(BaseModel):
    __tablename__ = "asset_tags"

    asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tag: Mapped[str] = mapped_column(String(100), nullable=False)


class AssetRelationship(BaseModel):
    __tablename__ = "asset_relationships"

    source_asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


class AssetHistory(BaseModel):
    __tablename__ = "asset_history"

    asset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
