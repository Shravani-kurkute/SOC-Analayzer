from datetime import datetime
from app.schemas.base import BaseSchema


class DashboardSummary(BaseSchema):
    total_logs_processed: int
    active_incidents: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    threat_score: float
    assets_monitored: int
    threat_intel_total: int = 0
    threat_intel_malicious: int = 0
    ai_investigations: int = 0
    avg_ai_confidence: float = 0.0
    total_incidents: int = 0
    open_incidents: int = 0
    critical_incidents: int = 0
    avg_resolution_seconds: int | None = None
    incidents_by_status: dict[str, int] = {}
    incidents_by_severity: dict[str, int] = {}


class ActivityPoint(BaseSchema):
    timestamp: str
    value: int


class DashboardActivity(BaseSchema):
    timeline: list[ActivityPoint]


class SeverityDistribution(BaseSchema):
    name: str
    value: int


class AttackTypeCount(BaseSchema):
    name: str
    count: int


class TopSourceIp(BaseSchema):
    ip: str
    count: int
    country: str | None = None


class MitreDistribution(BaseSchema):
    tactic: str
    count: int


class CountryDistribution(BaseSchema):
    country: str
    count: int


class DashboardCharts(BaseSchema):
    attack_timeline: list[ActivityPoint]
    alerts_by_severity: list[SeverityDistribution]
    attack_types: list[AttackTypeCount]
    top_source_ips: list[TopSourceIp]
    mitre_distribution: list[MitreDistribution]
    country_distribution: list[CountryDistribution]


class RecentAlertItem(BaseSchema):
    id: str
    title: str
    severity: str
    status: str
    source: str | None
    source_ip: str | None
    timestamp: datetime
    score: int


class RecentIncidentItem(BaseSchema):
    id: str
    title: str
    severity: str
    status: str
    category: str | None
    assignee_id: str | None
    created_at: datetime
    alert_count: int


class RecentLogItem(BaseSchema):
    id: str
    timestamp: datetime
    source_ip: str | None
    destination_ip: str | None
    action: str | None
    protocol: str | None
    log_source: str | None
    threat_score: int | None


class MostTargetedUser(BaseSchema):
    user_id: str
    email: str
    alert_count: int


class MostActiveSourceIp(BaseSchema):
    ip: str
    country: str | None
    log_count: int
    alert_count: int
