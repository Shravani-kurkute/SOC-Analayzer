from datetime import datetime, timezone, timedelta
from typing import Any
import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import async_session_factory
from app.models.threat_intel import ThreatIntel, ThreatProviderResult

logger = structlog.get_logger(__name__)

CACHE_TTL_HOURS = 24


async def get_cached(ioc_type: str, ioc_value: str, db: AsyncSession | None = None) -> ThreatIntel | None:
    async def _query(session):
        result = await session.execute(
            select(ThreatIntel).where(
                ThreatIntel.ioc_type == ioc_type,
                ThreatIntel.normalized_value == ioc_value.lower().strip(),
            )
        )
        return result.scalar_one_or_none()

    if db:
        entry = await _query(db)
    else:
        async with async_session_factory() as session:
            entry = await _query(session)
    if entry and entry.last_analysis:
        age = datetime.now(timezone.utc) - entry.last_analysis
        if age > timedelta(hours=CACHE_TTL_HOURS):
            return None
    return entry


async def get_provider_results(threat_intel_id: str, db: AsyncSession | None = None) -> list[ThreatProviderResult]:
    async def _query(session):
        result = await session.execute(
            select(ThreatProviderResult).where(
                ThreatProviderResult.threat_intel_id == threat_intel_id
            ).order_by(ThreatProviderResult.looked_up_at.desc())
        )
        return list(result.scalars().all())

    if db:
        return await _query(db)
    async with async_session_factory() as session:
        return await _query(session)


async def save_results(
    ioc_type: str,
    ioc_value: str,
    provider: str,
    result: dict[str, Any] | None,
    db: AsyncSession,
) -> ThreatIntel:
    normalized = ioc_value.lower().strip()
    existing = await get_cached(ioc_type, ioc_value, db)
    now = datetime.now(timezone.utc)

    if existing:
        entry = existing
        if result:
            entry.reputation_score = _calc_score(result)
            entry.confidence = result.get("confidence", entry.confidence)
            entry.malicious_count = result.get("malicious_count", entry.malicious_count)
            entry.harmless_count = result.get("harmless_count", entry.harmless_count)
            entry.suspicious_count = result.get("suspicious_count", entry.suspicious_count)
            entry.country = result.get("country") or entry.country
            entry.asn = result.get("asn") or entry.asn
            entry.asn_org = result.get("asn_org") or entry.asn_org
            entry.is_malicious = result.get("malicious", False) or entry.is_malicious
            entry.last_analysis = now
            if result.get("tags"):
                existing_tags = entry.tags or []
                all_tags = list(set(existing_tags + result["tags"]))
                entry.tags = all_tags
            if result.get("raw_response"):
                entry.raw_response = result["raw_response"]
    else:
        entry = ThreatIntel(
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            normalized_value=normalized,
            reputation_score=_calc_score(result) if result else 0.0,
            confidence=result.get("confidence", 0.0) if result else 0.0,
            malicious_count=result.get("malicious_count", 0) if result else 0,
            harmless_count=result.get("harmless_count", 0) if result else 0,
            suspicious_count=result.get("suspicious_count", 0) if result else 0,
            country=result.get("country") if result else None,
            asn=result.get("asn") if result else None,
            asn_org=result.get("asn_org") if result else None,
            is_malicious=result.get("malicious", False) if result else False,
            tags=result.get("tags") if result else None,
            first_seen=now,
            last_seen=now,
            last_analysis=now if result else None,
            raw_response=result.get("raw_response") if result else None,
        )
        db.add(entry)

    await db.flush()

    db.add(ThreatProviderResult(
        threat_intel_id=entry.id,
        provider=provider,
        reputation=result.get("reputation") if result else None,
        confidence=result.get("confidence", 0.0) if result else 0.0,
        malicious=result.get("malicious", False) if result else False,
        categories=result.get("categories") if result else None,
        raw_response=result.get("raw_response") if result else None,
        looked_up_at=now,
    ))

    await db.flush()
    await db.refresh(entry)
    return entry


def _calc_score(result: dict[str, Any] | None) -> float:
    if not result:
        return 0.0
    malicious = result.get("malicious_count", 0)
    suspicious = result.get("suspicious_count", 0)
    harmless = result.get("harmless_count", 0)
    total = malicious + suspicious + harmless
    if total == 0:
        return 0.5 if result.get("malicious") else 0.0
    return (malicious * 1.0 + suspicious * 0.5) / total
