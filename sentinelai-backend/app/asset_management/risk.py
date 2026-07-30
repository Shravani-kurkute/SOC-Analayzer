from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.asset import Asset, AssetRisk
from app.models.incident import Incident
from app.models.ioc_entry import IocEntry
from app.models.threat_intel import ThreatIntel


CRITICALITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.2,
}


async def calculate_asset_risk(db: AsyncSession, asset: Asset) -> float:
    asset_id = asset.id

    open_incidents_result = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.asset_ids.contains([asset_id]),
            Incident.status.notin_(["closed", "resolved"]),
        )
    )
    open_incidents = open_incidents_result.scalar() or 0

    critical_alerts_result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.asset_ids.contains([asset_id]),
            Alert.severity == "critical",
            Alert.status != "resolved",
        )
    )
    critical_alerts = critical_alerts_result.scalar() or 0

    threat_intel_result = await db.execute(
        select(func.count(ThreatIntel.id)).where(
            ThreatIntel.normalized_value.in_(
                select(IocEntry.normalized_value).where(IocEntry.source_ids.contains([asset_id]))
            ),
            ThreatIntel.is_malicious == True,
        )
    )
    threat_intel_matches = threat_intel_result.scalar() or 0

    cve_result = await db.execute(
        select(func.count(IocEntry.id)).where(
            IocEntry.ioc_type == "cve",
            IocEntry.source_ids.contains([asset_id]),
        )
    )
    cve_count = cve_result.scalar() or 0

    criticality_weight = CRITICALITY_WEIGHTS.get(asset.criticality, 0.5)

    exposure_score = 0.0
    if asset.open_ports and asset.open_ports > 0:
        exposure_score = min(1.0, asset.open_ports / 100)

    risk_score = (
        open_incidents * 15
        + critical_alerts * 20
        + threat_intel_matches * 10
        + cve_count * 8
        + exposure_score * 15
        + criticality_weight * 12
    )

    risk_score = min(100.0, risk_score)

    now = datetime.now(timezone.utc)
    existing = await db.execute(
        select(AssetRisk).where(AssetRisk.asset_id == asset_id)
    )
    risk_record = existing.scalar_one_or_none()

    if risk_record:
        risk_record.risk_score = risk_score
        risk_record.open_incidents = open_incidents
        risk_record.critical_alerts = critical_alerts
        risk_record.threat_intel_matches = threat_intel_matches
        risk_record.cve_count = cve_count
        risk_record.exposure_score = exposure_score
        risk_record.criticality_weight = criticality_weight
        risk_record.calculated_at = now
    else:
        risk_record = AssetRisk(
            asset_id=asset_id,
            risk_score=risk_score,
            open_incidents=open_incidents,
            critical_alerts=critical_alerts,
            threat_intel_matches=threat_intel_matches,
            cve_count=cve_count,
            exposure_score=exposure_score,
            criticality_weight=criticality_weight,
            calculated_at=now,
        )
        db.add(risk_record)

    asset.risk_score = risk_score

    return risk_score


def get_risk_level(score: float) -> str:
    if score >= 70:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 30:
        return "medium"
    return "low"
