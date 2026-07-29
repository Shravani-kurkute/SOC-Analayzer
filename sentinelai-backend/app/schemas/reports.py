from datetime import datetime
from app.schemas.base import BaseSchema


class ReportRequest(BaseSchema):
    report_type: str
    title: str
    format: str = "json"
    date_range_start: str | None = None
    date_range_end: str | None = None
    severity: str | None = None
    status: str | None = None
    mitre_technique: str | None = None
    incident_id: str | None = None
    analyst_id: str | None = None


class ReportResponse(BaseSchema):
    id: str
    report_type: str
    title: str
    format: str
    status: str
    file_path: str | None = None
    file_size: int | None = None
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    filters: dict | None = None
    data: dict | None = None
    download_count: int = 0
    generated_by_id: str | None = None
    created_at: datetime
    created_by: str | None = None


class ReportListItem(BaseSchema):
    id: str
    report_type: str
    title: str
    format: str
    status: str
    file_size: int | None = None
    download_count: int = 0
    generated_by_id: str | None = None
    created_at: datetime
    created_by: str | None = None


class ReportListResponse(BaseSchema):
    items: list[ReportListItem]
    total: int


class ScheduledReportRequest(BaseSchema):
    name: str
    report_type: str
    format: str = "pdf"
    cron_expression: str
    filters: dict | None = None
    recipients: list[str] | None = None


class ScheduledReportResponse(BaseSchema):
    id: str
    name: str
    report_type: str
    format: str
    cron_expression: str
    filters: dict | None = None
    recipients: list[str] | None = None
    is_active: bool
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_by_id: str | None = None
    created_at: datetime


class ReportStats(BaseSchema):
    total_reports: int
    reports_today: int
    most_downloaded: list[ReportListItem] = []
    recent_reports: list[ReportListItem] = []


class ExecutiveSOCReport(BaseSchema):
    report_type: str = "executive"
    generated_at: str
    date_range: dict | None = None
    executive_summary: str = ""
    total_incidents: int = 0
    critical_incidents: int = 0
    resolved_incidents: int = 0
    open_incidents: int = 0
    top_risks: list[dict] = []
    top_attack_types: list[dict] = []
    top_countries: list[dict] = []
    top_mitre_techniques: list[dict] = []
    avg_response_time_seconds: float | None = None
    avg_resolution_time_seconds: float | None = None
    soc_health_score: float = 0.0
    ai_summary: str = ""


class ThreatReportData(BaseSchema):
    report_type: str = "threat"
    generated_at: str
    date_range: dict | None = None
    attack_timeline: list[dict] = []
    ioc_summary: list[dict] = []
    threat_intelligence: list[dict] = []
    mitre_coverage: list[dict] = []
    attack_categories: list[dict] = []
    risk_distribution: list[dict] = []
    heatmap_data: list[dict] = []


class IncidentReportData(BaseSchema):
    report_type: str = "incident"
    generated_at: str
    incident_id: str
    incident_title: str
    severity: str
    status: str
    description: str | None = None
    timeline: list[dict] = []
    comments: list[dict] = []
    evidence: list[dict] = []
    tasks: list[dict] = []
    ai_investigation: dict | None = None
    mitre_mapping: list[dict] = []
    threat_intel: list[dict] = []


class AssetReportData(BaseSchema):
    report_type: str = "asset"
    generated_at: str
    assets: list[dict] = []
    asset_summary: dict = {}
    criticality_distribution: list[dict] = []
    incidents_by_asset: list[dict] = []
    open_risks: list[dict] = []


class ComplianceReportData(BaseSchema):
    report_type: str = "compliance"
    generated_at: str
    soc2_coverage: dict = {}
    iso27001_coverage: dict = {}
    nist_coverage: dict = {}
    cis_coverage: dict = {}
    mitre_coverage_summary: dict = {}
    controls_coverage: list[dict] = []
