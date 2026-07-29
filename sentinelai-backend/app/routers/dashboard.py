from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.ai_investigation import AIInvestigation
from app.models.alert import Alert
from app.models.asset import Asset
from app.models.incident import Incident
from app.models.log_entry import LogEntry
from app.models.threat_intel import ThreatIntel
from app.models.user import User
from app.schemas.dashboard import (
    DashboardActivity,
    DashboardCharts,
    DashboardSummary,
    MostActiveSourceIp,
    MostTargetedUser,
    RecentAlertItem,
    RecentIncidentItem,
    RecentLogItem,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    total_logs = await db.scalar(select(func.count(LogEntry.id)))
    active_incidents = await db.scalar(
        select(func.count(Incident.id)).where(Incident.status.in_(["open", "investigating", "contained"]))
    )
    critical = await db.scalar(
        select(func.count(Alert.id)).where(Alert.severity == "critical", Alert.status != "resolved")
    )
    high = await db.scalar(
        select(func.count(Alert.id)).where(Alert.severity == "high", Alert.status != "resolved")
    )
    medium = await db.scalar(
        select(func.count(Alert.id)).where(Alert.severity == "medium", Alert.status != "resolved")
    )
    low = await db.scalar(
        select(func.count(Alert.id)).where(Alert.severity == "low", Alert.status != "resolved")
    )
    total_alerts = (critical or 0) + (high or 0) + (medium or 0) + (low or 0)
    threat_score = min(100.0, (total_alerts / max((await db.scalar(select(func.count(Alert.id)))) or 1, 1)) * 100) if total_alerts > 0 else 0.0
    assets_monitored = await db.scalar(select(func.count(Asset.id)))

    ti_total = await db.scalar(select(func.count(ThreatIntel.id)))
    ti_malicious = await db.scalar(
        select(func.count(ThreatIntel.id)).where(ThreatIntel.is_malicious == True)
    )

    ai_total = await db.scalar(select(func.count(AIInvestigation.id)))
    avg_ai_conf = await db.scalar(
        select(func.avg(AIInvestigation.confidence_score))
        .where(AIInvestigation.confidence_score.isnot(None))
    )

    return DashboardSummary(
        total_logs_processed=total_logs or 0,
        active_incidents=active_incidents or 0,
        critical_alerts=critical or 0,
        high_alerts=high or 0,
        medium_alerts=medium or 0,
        low_alerts=low or 0,
        threat_score=round(threat_score, 1),
        assets_monitored=assets_monitored or 0,
        threat_intel_total=ti_total or 0,
        threat_intel_malicious=ti_malicious or 0,
        ai_investigations=ai_total or 0,
        avg_ai_confidence=round(float(avg_ai_conf or 0.0), 4),
    )


@router.get("/activity")
async def get_dashboard_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    hours = 24
    points = []
    for i in range(hours, -1, -1):
        label = f"{i:02d}:00"
        start = text(f"NOW() - INTERVAL '{i+1} hours'")
        end = text(f"NOW() - INTERVAL '{i} hours'")
        count = await db.scalar(
            select(func.count(Alert.id)).where(
                Alert.created_at >= start,
                Alert.created_at < end,
            )
        )
        points.append({"timestamp": label, "value": count or 0})
    return DashboardActivity(timeline=points)


@router.get("/charts")
async def get_dashboard_charts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    alerts_by_severity = (
        await db.execute(
            select(Alert.severity, func.count(Alert.id).label("count"))
            .group_by(Alert.severity)
            .order_by(Alert.severity)
        )
    ).all()

    attack_types_result = (
        await db.execute(
            select(Alert.mitre_tactic, func.count(Alert.id).label("count"))
            .where(Alert.mitre_tactic.isnot(None))
            .group_by(Alert.mitre_tactic)
            .order_by(func.count(Alert.id).desc())
            .limit(10)
        )
    ).all()

    top_ips = (
        await db.execute(
            select(Alert.source_ip, func.count(Alert.id).label("count"), Alert.country)
            .where(Alert.source_ip.isnot(None))
            .group_by(Alert.source_ip, Alert.country)
            .order_by(func.count(Alert.id).desc())
            .limit(10)
        )
    ).all()

    mitre = (
        await db.execute(
            select(Alert.mitre_tactic, func.count(Alert.id).label("count"))
            .where(Alert.mitre_tactic.isnot(None))
            .group_by(Alert.mitre_tactic)
            .order_by(func.count(Alert.id).desc())
        )
    ).all()

    countries = (
        await db.execute(
            select(Alert.country, func.count(Alert.id).label("count"))
            .where(Alert.country.isnot(None))
            .group_by(Alert.country)
            .order_by(func.count(Alert.id).desc())
        )
    ).all()

    hours = 24
    timeline = []
    for i in range(hours, -1, -1):
        start = text(f"NOW() - INTERVAL '{i+1} hours'")
        end = text(f"NOW() - INTERVAL '{i} hours'")
        count = await db.scalar(
            select(func.count(Alert.id)).where(
                Alert.created_at >= start,
                Alert.created_at < end,
            )
        )
        timeline.append({"timestamp": f"{i:02d}:00", "value": count or 0})

    return DashboardCharts(
        attack_timeline=timeline,
        alerts_by_severity=[{"name": s.severity, "value": s.count} for s in alerts_by_severity],
        attack_types=[{"name": t.mitre_tactic, "count": t.count} for t in attack_types_result],
        top_source_ips=[{"ip": ip.source_ip, "country": ip.country, "count": ip.count} for ip in top_ips],
        mitre_distribution=[{"tactic": m.mitre_tactic, "count": m.count} for m in mitre],
        country_distribution=[{"country": c.country, "count": c.count} for c in countries],
    )


@router.get("/recent-alerts")
async def get_recent_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    result = (
        await db.execute(
            select(Alert)
            .order_by(Alert.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()

    return [
        RecentAlertItem(
            id=a.id,
            title=a.title,
            severity=a.severity,
            status=a.status,
            source=a.source,
            source_ip=a.source_ip,
            timestamp=a.created_at,
            score=a.score,
        )
        for a in result
    ]


@router.get("/recent-incidents")
async def get_recent_incidents(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    result = (
        await db.execute(
            select(Incident)
            .order_by(Incident.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()

    return [
        RecentIncidentItem(
            id=i.id,
            title=i.title,
            severity=i.severity,
            status=i.status,
            category=i.category,
            assignee_id=i.assignee_id,
            created_at=i.created_at,
            alert_count=len(i.alert_ids) if i.alert_ids else 0,
        )
        for i in result
    ]


@router.get("/recent-logs")
async def get_recent_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    result = (
        await db.execute(
            select(LogEntry)
            .order_by(LogEntry.timestamp.desc())
            .limit(limit)
        )
    ).scalars().all()

    return [
        RecentLogItem(
            id=log.id,
            timestamp=log.timestamp,
            source_ip=log.source_ip,
            destination_ip=log.destination_ip,
            action=log.action,
            protocol=log.protocol,
            log_source=log.log_source,
            threat_score=log.threat_score,
        )
        for log in result
    ]


@router.get("/most-targeted-users")
async def get_most_targeted_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    result = (
        await db.execute(
            select(User.id, User.email, func.count(Alert.id).label("alert_count"))
            .join(Alert, Alert.destination_ip == User.email, isouter=True)
            .group_by(User.id, User.email)
            .order_by(func.count(Alert.id).desc())
            .limit(limit)
        )
    ).all()

    return [
        MostTargetedUser(user_id=r.id, email=r.email, alert_count=r.alert_count)
        for r in result
    ]


@router.get("/most-active-ips")
async def get_most_active_ips(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    log_counts = (
        await db.execute(
            select(LogEntry.source_ip, func.count(LogEntry.id).label("log_count"))
            .where(LogEntry.source_ip.isnot(None))
            .group_by(LogEntry.source_ip)
            .order_by(func.count(LogEntry.id).desc())
            .limit(limit)
        )
    ).all()

    ips = [r.source_ip for r in log_counts]
    alert_counts = {r.source_ip: r.alert_count for r in (
        await db.execute(
            select(Alert.source_ip, func.count(Alert.id).label("alert_count"))
            .where(Alert.source_ip.in_(ips))
            .group_by(Alert.source_ip)
        )
    ).all()} if ips else {}

    result = []
    for r in log_counts:
        country_row = (
            await db.execute(
                select(LogEntry.country)
                .where(LogEntry.source_ip == r.source_ip, LogEntry.country.isnot(None))
                .limit(1)
            )
        ).scalar_one_or_none()

        result.append(
            MostActiveSourceIp(
                ip=r.source_ip,
                country=country_row,
                log_count=r.log_count,
                alert_count=alert_counts.get(r.source_ip, 0),
            )
        )

    return result
