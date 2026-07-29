from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_timeline import IncidentTimeline


async def add_timeline_entry(
    db: AsyncSession,
    incident_id: str,
    action: str,
    actor: str,
    details: str | None = None,
    metadata_json: dict | None = None,
) -> IncidentTimeline:
    entry = IncidentTimeline(
        incident_id=incident_id,
        action=action,
        actor=actor,
        details=details,
        metadata_json=metadata_json,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def get_timeline(db: AsyncSession, incident_id: str) -> list[IncidentTimeline]:
    result = await db.execute(
        select(IncidentTimeline)
        .where(IncidentTimeline.incident_id == incident_id)
        .order_by(IncidentTimeline.created_at.asc())
    )
    return list(result.scalars().all())
