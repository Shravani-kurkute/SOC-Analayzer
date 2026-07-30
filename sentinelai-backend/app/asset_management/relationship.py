from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetRelationship
from app.models.ai_investigation import AIInvestigation
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.ioc_entry import IocEntry
from app.models.threat_intel import ThreatIntel


async def get_related_incidents(db: AsyncSession, asset_id: str) -> Sequence[Incident]:
    result = await db.execute(
        select(Incident)
        .where(Incident.asset_ids.contains([asset_id]))
        .order_by(Incident.created_at.desc())
    )
    return result.scalars().all()


async def get_related_alerts(db: AsyncSession, asset_id: str) -> Sequence[Alert]:
    result = await db.execute(
        select(Alert)
        .where(Alert.asset_ids.contains([asset_id]))
        .order_by(Alert.created_at.desc())
    )
    return result.scalars().all()


async def get_related_iocs(db: AsyncSession, asset_id: str) -> Sequence[IocEntry]:
    result = await db.execute(
        select(IocEntry)
        .where(IocEntry.source_ids.contains([asset_id]))
        .order_by(IocEntry.created_at.desc())
    )
    return result.scalars().all()


async def get_related_threat_intel(db: AsyncSession, asset_id: str) -> Sequence[ThreatIntel]:
    result = await db.execute(
        select(ThreatIntel)
        .where(ThreatIntel.normalized_value.in_(
            select(IocEntry.normalized_value).where(IocEntry.source_ids.contains([asset_id]))
        ))
        .order_by(ThreatIntel.created_at.desc())
    )
    return result.scalars().all()


async def get_related_ai_reports(db: AsyncSession, asset_id: str) -> Sequence[AIInvestigation]:
    incident_ids_subquery = select(Incident.id).where(Incident.asset_ids.contains([asset_id]))
    result = await db.execute(
        select(AIInvestigation)
        .where(AIInvestigation.incident_id.in_(incident_ids_subquery))
        .order_by(AIInvestigation.created_at.desc())
    )
    return result.scalars().all()


async def get_asset_relationships(db: AsyncSession, asset_id: str) -> list[dict[str, Any]]:
    result = await db.execute(
        select(AssetRelationship).where(
            (AssetRelationship.source_asset_id == asset_id) |
            (AssetRelationship.target_asset_id == asset_id)
        )
    )
    relationships = result.scalars().all()

    related_ids = set()
    for rel in relationships:
        related_ids.add(rel.source_asset_id)
        related_ids.add(rel.target_asset_id)
    related_ids.discard(asset_id)

    related_assets = {}
    if related_ids:
        assets_result = await db.execute(
            select(Asset).where(Asset.id.in_(list(related_ids)))
        )
        for a in assets_result.scalars().all():
            related_assets[a.id] = {
                "id": a.id,
                "hostname": a.hostname,
                "ip_address": a.ip_address,
                "asset_type": a.asset_type,
                "criticality": a.criticality,
            }

    result_list = []
    for rel in relationships:
        is_source = rel.source_asset_id == asset_id
        target_id = rel.target_asset_id if is_source else rel.source_asset_id
        result_list.append({
            "id": rel.id,
            "source_asset_id": rel.source_asset_id,
            "target_asset_id": rel.target_asset_id,
            "relationship_type": rel.relationship_type,
            "direction": "outgoing" if is_source else "incoming",
            "target": related_assets.get(target_id, {"id": target_id}),
        })

    return result_list


async def create_relationship(db: AsyncSession, source_id: str, target_id: str, rel_type: str, md: dict | None = None) -> AssetRelationship:
    rel = AssetRelationship(
        source_asset_id=source_id,
        target_asset_id=target_id,
        relationship_type=rel_type,
        metadata_json=md,
    )
    db.add(rel)
    await db.flush()
    return rel


async def get_asset_stats(db: AsyncSession) -> dict[str, Any]:
    from sqlalchemy import func, select

    total = await db.scalar(select(func.count(Asset.id))) or 0
    healthy = await db.scalar(
        select(func.count(Asset.id)).where(Asset.status == "online")
    ) or 0
    critical = await db.scalar(
        select(func.count(Asset.id)).where(Asset.criticality == "critical")
    ) or 0
    offline = await db.scalar(
        select(func.count(Asset.id)).where(Asset.status == "offline")
    ) or 0
    high_risk = await db.scalar(
        select(func.count(Asset.id)).where(Asset.risk_score >= 50)
    ) or 0

    dept_result = await db.execute(
        select(Asset.department, func.count(Asset.id)).where(Asset.department.isnot(None)).group_by(Asset.department)
    )
    by_department = dict(dept_result.all())

    os_result = await db.execute(
        select(Asset.os, func.count(Asset.id)).where(Asset.os.isnot(None)).group_by(Asset.os)
    )
    by_os = dict(os_result.all())

    type_result = await db.execute(
        select(Asset.asset_type, func.count(Asset.id)).group_by(Asset.asset_type)
    )
    by_type = dict(type_result.all())

    status_result = await db.execute(
        select(Asset.status, func.count(Asset.id)).group_by(Asset.status)
    )
    by_status = dict(status_result.all())

    crit_result = await db.execute(
        select(Asset.criticality, func.count(Asset.id)).group_by(Asset.criticality)
    )
    by_criticality = dict(crit_result.all())

    risk_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    risk_result = await db.execute(
        select(Asset.risk_score)
    )
    for score in risk_result.scalars().all():
        if score >= 70:
            risk_dist["critical"] += 1
        elif score >= 50:
            risk_dist["high"] += 1
        elif score >= 30:
            risk_dist["medium"] += 1
        else:
            risk_dist["low"] += 1

    return {
        "total_assets": total,
        "healthy_assets": healthy,
        "critical_assets": critical,
        "offline_assets": offline,
        "high_risk_assets": high_risk,
        "by_department": by_department,
        "by_os": by_os,
        "by_type": by_type,
        "by_status": by_status,
        "by_criticality": by_criticality,
        "risk_distribution": risk_dist,
    }
