from datetime import datetime
from typing import Any

from pydantic import Field
from app.schemas.base import BaseSchema


class AssetCreate(BaseSchema):
    hostname: str
    ip_address: str | None = None
    mac_address: str | None = None
    os: str | None = None
    os_version: str | None = None
    asset_type: str = "server"
    criticality: str = "medium"
    environment: str | None = None
    status: str = "unknown"
    tags: list[str] | None = None
    location: str | None = None
    department: str | None = None
    owner: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    notes: str | None = None


class AssetUpdate(BaseSchema):
    hostname: str | None = None
    ip_address: str | None = None
    mac_address: str | None = None
    os: str | None = None
    os_version: str | None = None
    asset_type: str | None = None
    criticality: str | None = None
    environment: str | None = None
    status: str | None = None
    tags: list[str] | None = None
    location: str | None = None
    department: str | None = None
    owner: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    notes: str | None = None


class AssetResponse(BaseSchema):
    id: str
    hostname: str
    ip_address: str | None = None
    mac_address: str | None = None
    os: str | None = None
    os_version: str | None = None
    asset_type: str
    criticality: str
    environment: str | None = None
    status: str
    tags: list[str] | None = None
    vulnerability_count: int = 0
    open_ports: int = 0
    last_seen: datetime | None = None
    location: str | None = None
    department: str | None = None
    owner: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    notes: str | None = None
    risk_score: float = 0.0
    discovery_source: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None


class AssetListItem(BaseSchema):
    id: str
    hostname: str
    ip_address: str | None = None
    os: str | None = None
    asset_type: str
    criticality: str
    status: str
    risk_score: float = 0.0
    department: str | None = None
    owner: str | None = None
    vulnerability_count: int = 0
    last_seen: datetime | None = None
    created_at: datetime


class AssetDetailResponse(AssetResponse):
    risk_details: dict[str, Any] | None = None
    incident_count: int = 0
    alert_count: int = 0
    ioc_count: int = 0
    threat_intel_count: int = 0
    ai_report_count: int = 0
    relationships: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []


class AssetStats(BaseSchema):
    total_assets: int = 0
    healthy_assets: int = 0
    critical_assets: int = 0
    offline_assets: int = 0
    high_risk_assets: int = 0
    by_department: dict[str, int] = {}
    by_os: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_criticality: dict[str, int] = {}
    risk_distribution: dict[str, int] = {}


class AssetRelationshipCreate(BaseSchema):
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    metadata_json: dict[str, Any] | None = None


class AssetImportResult(BaseSchema):
    imported: int = 0
    updated: int = 0
    failed: int = 0
    errors: list[str] = []
