from datetime import datetime
from typing import Any
from app.schemas.base import BaseSchema


class ProviderResultSchema(BaseSchema):
    name: str
    reputation: str | None = None
    confidence: float = 0.0
    malicious: bool = False
    categories: dict[str, Any] | None = None
    looked_up_at: str | None = None


class ThreatIntelResponse(BaseSchema):
    id: str
    ioc_type: str
    ioc_value: str
    normalized_value: str
    reputation_score: float
    confidence: float
    is_malicious: bool
    malicious_count: int = 0
    harmless_count: int = 0
    suspicious_count: int = 0
    country: str | None = None
    asn: str | None = None
    asn_org: str | None = None
    tags: list[str] | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    last_analysis: str | None = None
    cached: bool = False
    providers: list[ProviderResultSchema] = []


class ThreatIntelListResponse(BaseSchema):
    id: str
    ioc_type: str
    ioc_value: str
    normalized_value: str
    reputation_score: float
    is_malicious: bool
    malicious_count: int = 0
    country: str | None = None
    asn: str | None = None
    last_analysis: str | None = None
    tags: list[str] | None = None


class ThreatIntelStatsResponse(BaseSchema):
    total_iocs: int = 0
    malicious_count: int = 0
    harmless_count: int = 0
    by_type: dict[str, int] = {}
    provider_stats: dict[str, int] = {}
    recent_lookups: list[dict[str, Any]] = []


class LookupRequest(BaseSchema):
    ioc_type: str
    ioc_value: str
