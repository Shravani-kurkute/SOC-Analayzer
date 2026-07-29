from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema


class IocEntryResponse(BaseSchema):
    id: str
    ioc_type: str
    ioc_value: str
    normalized_value: str
    confidence: float
    source_event: str | None = None
    source_log: str | None = None
    source_ip: str | None = None
    first_seen: datetime
    last_seen: datetime
    occurrences: int
    severity: str
    status: str
    tags: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = Field(None, validation_alias="extra_data")
    source_ids: list[str] | None = None
    context: str | None = None
    kill_chain_phase: str | None = None
    created_at: datetime
    updated_at: datetime


class IocStatsResponse(BaseSchema):
    total: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    by_status: dict[str, int]
    top_source_ips: list[dict[str, Any]]
    latest_iocs: list[dict[str, Any]]
    unique_domains: int
    unique_ips: int
    unique_hashes: int


class IocExtractResponse(BaseSchema):
    extracted: int
    new: int
    updated: int
    iocs: list[IocEntryResponse]


class IocSearchParams(BaseSchema):
    q: str | None = None
    ioc_type: str | None = None
    severity: str | None = None
    status: str | None = None
    source_ip: str | None = None
    source_log: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "last_seen"
    sort_order: str = "desc"
