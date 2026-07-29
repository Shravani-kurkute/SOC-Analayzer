from datetime import datetime, timezone
from sqlalchemy import func, select, extract, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.models.asset import Asset
from app.models.ioc_entry import IocEntry
from app.models.threat_intel import ThreatIntel
from app.models.mitre_technique import MitreTechnique, MitreMapping, CoverageStatistic
from app.models.incident_comment import IncidentComment
from app.models.incident_task import IncidentTask
from app.models.incident_evidence import IncidentEvidence
from app.models.incident_timeline import IncidentTimeline
from app.models.ai_investigation import AIInvestigation
from app.models.user import User


async def build_executive_report(db: AsyncSession, filters: dict | None = None) -> dict:
    date_start = filters.get("date_range_start") if filters else None
    date_end = filters.get("date_range_end") if filters else None

    base = select(Incident)
    if date_start:
        base = base.where(Incident.created_at >= date_start)
    if date_end:
        base = base.where(Incident.created_at <= date_end)

    total = (await db.scalar(select(func.count(Incident.id)).where(base.where_clause if base.where_clause is not None else True).select_from(Incident))) or 0
    critical = (await db.scalar(select(func.count(Incident.id)).where(Incident.severity == "critical"))) or 0
    resolved = (await db.scalar(select(func.count(Incident.id)).where(Incident.status.in_(["closed", "resolved"])))) or 0
    open_count = (await db.scalar(select(func.count(Incident.id)).where(Incident.status.notin_(["closed", "resolved"])))) or 0

    top_risks_raw = (await db.execute(
        select(Incident.category, func.count(Incident.id).label("count"))
        .where(Incident.category.isnot(None))
        .group_by(Incident.category)
        .order_by(func.count(Incident.id).desc())
        .limit(10)
    )).all()

    top_attacks_raw = (await db.execute(
        select(Alert.mitre_tactic, func.count(Alert.id).label("count"))
        .where(Alert.mitre_tactic.isnot(None))
        .group_by(Alert.mitre_tactic)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )).all()

    top_countries_raw = (await db.execute(
        select(Alert.country, func.count(Alert.id).label("count"))
        .where(Alert.country.isnot(None))
        .group_by(Alert.country)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )).all()

    top_mitre_raw = (await db.execute(
        select(MitreMapping.technique_id, func.count(MitreMapping.incident_id).label("count"))
        .group_by(MitreMapping.technique_id)
        .order_by(func.count(MitreMapping.incident_id).desc())
        .limit(10)
    )).all()

    avg_response = await db.scalar(
        select(func.avg(extract("epoch", Incident.updated_at - Incident.created_at)))
        .where(Incident.status != "new")
    )

    avg_resolution = await db.scalar(
        select(func.avg(extract("epoch", Incident.closed_at - Incident.created_at)))
        .where(Incident.closed_at.isnot(None))
    )

    total_alerts = (await db.scalar(select(func.count(Alert.id)))) or 1
    resolved_alerts = (await db.scalar(select(func.count(Alert.id)).where(Alert.status == "resolved"))) or 0
    health = round((resolved_alerts / total_alerts) * 100, 1) if total_alerts > 0 else 0.0

    ai_summary = f"SOC processed {total} incidents with {critical} critical. Health score: {health}%."

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executive_summary": "",
        "total_incidents": total,
        "critical_incidents": critical,
        "resolved_incidents": resolved,
        "open_incidents": open_count,
        "top_risks": [{"name": r[0], "count": r[1]} for r in top_risks_raw],
        "top_attack_types": [{"name": r[0], "count": r[1]} for r in top_attacks_raw],
        "top_countries": [{"name": r[0], "count": r[1]} for r in top_countries_raw],
        "top_mitre_techniques": [{"technique": r[0], "count": r[1]} for r in top_mitre_raw],
        "avg_response_time_seconds": float(avg_response) if avg_response else None,
        "avg_resolution_time_seconds": float(avg_resolution) if avg_resolution else None,
        "soc_health_score": health,
        "ai_summary": ai_summary,
    }


async def build_threat_report(db: AsyncSession, filters: dict | None = None) -> dict:
    date_start = filters.get("date_range_start") if filters else None
    date_end = filters.get("date_range_end") if filters else None

    alert_base = select(Alert)
    if date_start:
        alert_base = alert_base.where(Alert.created_at >= date_start)
    if date_end:
        alert_base = alert_base.where(Alert.created_at <= date_end)

    timeline_raw = (await db.execute(
        select(func.date_trunc("hour", Alert.created_at).label("hour"), func.count(Alert.id))
        .group_by(text("hour"))
        .order_by(text("hour"))
        .limit(168)
    )).all() if hasattr(Alert, "created_at") else []

    ioc_raw = (await db.execute(
        select(IocEntry.ioc_type, func.count(IocEntry.id).label("count"))
        .group_by(IocEntry.ioc_type)
        .order_by(func.count(IocEntry.id).desc())
    )).all()

    ti_raw = (await db.execute(
        select(ThreatIntel.ioc_type, func.count(ThreatIntel.id).label("count"))
        .group_by(ThreatIntel.ioc_type)
        .order_by(func.count(ThreatIntel.id).desc())
        .limit(10)
    )).all()

    mitre_raw = (await db.execute(
        select(MitreMapping.tactic, func.count(MitreMapping.id).label("count"))
        .group_by(MitreMapping.tactic)
        .order_by(func.count(MitreMapping.id).desc())
    )).all()

    categories_raw = (await db.execute(
        select(Alert.category, func.count(Alert.id).label("count"))
        .where(Alert.category.isnot(None))
        .group_by(Alert.category)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )).all()

    risk_raw = (await db.execute(
        select(Alert.severity, func.count(Alert.id).label("count"))
        .group_by(Alert.severity)
    )).all()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "attack_timeline": [{"time": str(r[0]), "count": r[1]} for r in timeline_raw],
        "ioc_summary": [{"type": r[0], "count": r[1]} for r in ioc_raw],
        "threat_intelligence": [{"type": r[0], "count": r[1]} for r in ti_raw],
        "mitre_coverage": [{"tactic": r[0], "count": r[1]} for r in mitre_raw],
        "attack_categories": [{"name": r[0], "count": r[1]} for r in categories_raw],
        "risk_distribution": [{"name": r[0], "count": r[1]} for r in risk_raw],
        "heatmap_data": [],
    }


async def build_incident_report(db: AsyncSession, incident_id: str) -> dict:
    incident = (await db.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
    if not incident:
        raise ValueError("Incident not found")

    comments = (await db.execute(
        select(IncidentComment).where(IncidentComment.incident_id == incident_id).order_by(IncidentComment.created_at)
    )).scalars().all()

    tasks = (await db.execute(
        select(IncidentTask).where(IncidentTask.incident_id == incident_id).order_by(IncidentTask.created_at)
    )).scalars().all()

    evidence = (await db.execute(
        select(IncidentEvidence).where(IncidentEvidence.incident_id == incident_id)
    )).scalars().all()

    timeline = (await db.execute(
        select(IncidentTimeline).where(IncidentTimeline.incident_id == incident_id).order_by(IncidentTimeline.created_at)
    )).scalars().all()

    ai_report = (await db.execute(
        select(AIInvestigation).where(AIInvestigation.incident_id == incident_id).order_by(AIInvestigation.created_at.desc()).limit(1)
    )).scalar_one_or_none()

    mitre_mappings = (await db.execute(
        select(MitreMapping).where(MitreMapping.incident_id == incident_id)
    )).scalars().all() if hasattr(MitreMapping, "incident_id") else []

    threat_intel_raw = (await db.execute(
        select(ThreatIntel).limit(10)
    )).scalars().all()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident_id": incident.id,
        "incident_title": incident.title,
        "severity": incident.severity,
        "status": incident.status,
        "description": incident.description,
        "timeline": [{"id": t.id, "action": t.action, "actor": t.actor, "details": t.details, "created_at": t.created_at.isoformat()} for t in timeline],
        "comments": [{"id": c.id, "author_name": c.author_name, "content": c.content, "created_at": c.created_at.isoformat()} for c in comments],
        "evidence": [{"id": e.id, "filename": e.filename, "file_type": e.file_type, "file_size": e.file_size, "sha256": e.sha256} for e in evidence],
        "tasks": [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "assignee_name": t.assignee_name, "due_date": t.due_date.isoformat() if t.due_date else None} for t in tasks],
        "ai_investigation": {"summary": ai_report.summary, "confidence_score": ai_report.confidence_score, "root_cause": ai_report.root_cause} if ai_report else None,
        "mitre_mapping": [{"technique_id": m.technique_id, "tactic": m.tactic} for m in mitre_mappings],
        "threat_intel": [{"id": t.id, "ioc_value": t.ioc_value, "ioc_type": t.ioc_type, "is_malicious": t.is_malicious} for t in threat_intel_raw],
    }


async def build_asset_report(db: AsyncSession) -> dict:
    assets = (await db.execute(select(Asset))).scalars().all()
    total_assets = len(assets)

    criticality_raw = (await db.execute(
        select(Asset.criticality, func.count(Asset.id).label("count"))
        .where(Asset.criticality.isnot(None))
        .group_by(Asset.criticality)
    )).all()

    incidents_by_asset_raw = []
    for asset in assets[:20]:
        if asset.id:
            count = (await db.scalar(
                select(func.count(Incident.id)).where(Incident.asset_ids.contains([asset.id]))
            )) or 0
            if count > 0:
                incidents_by_asset_raw.append({"asset_id": asset.id, "name": asset.name, "incident_count": count})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": [{"id": a.id, "name": a.name, "type": getattr(a, "asset_type", None), "criticality": a.criticality, "owner": a.owner} for a in assets],
        "asset_summary": {"total": total_assets, "with_incidents": len(incidents_by_asset_raw)},
        "criticality_distribution": [{"name": r[0], "count": r[1]} for r in criticality_raw],
        "incidents_by_asset": sorted(incidents_by_asset_raw, key=lambda x: x["incident_count"], reverse=True)[:20],
        "open_risks": [],
    }


async def build_compliance_report(db: AsyncSession) -> dict:
    mitre_raw = (await db.execute(
        select(MitreTechnique.tactic, func.count(MitreTechnique.technique_id).label("covered"))
        .select_from(MitreTechnique)
        .group_by(MitreTechnique.tactic)
    )).all()

    total_techniques_raw = (await db.execute(
        select(func.count(MitreTechnique.technique_id))
    )).scalar() or 0

    covered_techniques = len(mitre_raw)
    coverage_pct = round((covered_techniques / max(total_techniques_raw, 1)) * 100, 1)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "soc2_coverage": {"status": "partial", "percentage": coverage_pct},
        "iso27001_coverage": {"status": "partial", "percentage": coverage_pct},
        "nist_coverage": {"status": "partial", "percentage": coverage_pct},
        "cis_coverage": {"status": "partial", "percentage": coverage_pct},
        "mitre_coverage_summary": {"total_techniques": total_techniques_raw, "covered": covered_techniques, "percentage": coverage_pct},
        "controls_coverage": [{"tactic": r[0], "covered": r[1]} for r in mitre_raw],
    }
