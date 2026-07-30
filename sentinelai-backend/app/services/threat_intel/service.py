from datetime import datetime, timezone
from typing import Any
import structlog
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.session import async_session_factory
from app.models.threat_intel import ThreatIntel, ThreatProviderResult, LookupHistory
from app.services.threat_intel.providers import (
    MockProvider, VirusTotalProvider, AbuseIPDBProvider, AlienVaultProvider, BaseProvider,
)
from app.services.threat_intel.cache import get_cached, save_results

logger = structlog.get_logger(__name__)


class ThreatIntelligenceService:
    def __init__(self):
        self.providers: list[BaseProvider] = []
        self._init_providers()

    def _init_providers(self):
        providers_config = [
            (MockProvider, None, True),
            (VirusTotalProvider, settings.VIRUSTOTAL_API_KEY, settings.VIRUSTOTAL_ENABLED),
            (AbuseIPDBProvider, settings.ABUSEIPDB_API_KEY, settings.ABUSEIPDB_ENABLED),
            (AlienVaultProvider, settings.ALIENVAULT_API_KEY, settings.ALIENVAULT_ENABLED),
        ]
        for provider_cls, api_key, enabled in providers_config:
            if api_key or provider_cls == MockProvider:
                inst = provider_cls(api_key) if api_key else provider_cls()
                inst.enabled = enabled
                self.providers.append(inst)

    async def lookup(self, ioc_type: str, ioc_value: str, db: AsyncSession | None = None) -> dict[str, Any]:
        if db:
            return await self._lookup_with_db(ioc_type, ioc_value, db)
        async with async_session_factory() as session:
            return await self._lookup_with_db(ioc_type, ioc_value, session)

    async def _lookup_with_db(self, ioc_type: str, ioc_value: str, db: AsyncSession) -> dict[str, Any]:
        cached = await get_cached(ioc_type, ioc_value, db)
        if cached:
            results = await self._get_provider_results(cached.id, db)
            return self._build_response(cached, results, cached=True)

        combined_results: list[dict[str, Any]] = []
        lookup_histories: list[LookupHistory] = []
        for provider in self.providers:
            if not provider.is_enabled():
                continue
            start = datetime.now(timezone.utc)
            try:
                result = await provider.lookup(ioc_type, ioc_value)
                elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
                success = result is not None
                if result:
                    combined_results.append(result)
                lookup_histories.append(LookupHistory(
                    ioc_type=ioc_type, ioc_value=ioc_value,
                    provider=provider.name, success=success,
                    response_time_ms=elapsed,
                    looked_up_at=datetime.now(timezone.utc),
                ))
            except Exception as e:
                logger.error("Provider lookup failed", provider=provider.name, error=str(e))
                lookup_histories.append(LookupHistory(
                    ioc_type=ioc_type, ioc_value=ioc_value,
                    provider=provider.name, success=False,
                    error_message=str(e),
                    looked_up_at=datetime.now(timezone.utc),
                ))

        merged = self._merge_results(combined_results)
        entry = await save_results(ioc_type, ioc_value, "merged", merged, db)
        for lh in lookup_histories:
            lh.threat_intel_id = entry.id
            db.add(lh)
        await db.commit()
        results = await self._get_provider_results(entry.id, db)
        return self._build_response(entry, results, cached=False)

    async def _get_provider_results(self, threat_intel_id: str, db: AsyncSession) -> list[ThreatProviderResult]:
        result = await db.execute(
            select(ThreatProviderResult).where(
                ThreatProviderResult.threat_intel_id == threat_intel_id
            ).order_by(ThreatProviderResult.looked_up_at.desc())
        )
        return list(result.scalars().all())

    def _merge_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {"reputation": "unknown", "confidence": 0.0, "malicious": False}
        malicious = any(r.get("malicious", False) for r in results)
        malicious_count = sum(r.get("malicious_count", 0) for r in results)
        harmless_count = sum(r.get("harmless_count", 0) for r in results)
        suspicious_count = sum(r.get("suspicious_count", 0) for r in results)
        confidence = max(r.get("confidence", 0.0) for r in results)
        country = next((r.get("country") for r in results if r.get("country")), None)
        asn = next((r.get("asn") for r in results if r.get("asn")), None)
        asn_org = next((r.get("asn_org") for r in results if r.get("asn_org")), None)
        all_tags = []
        for r in results:
            tags = r.get("tags", [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        return {
            "reputation": "malicious" if malicious else "harmless",
            "confidence": confidence,
            "malicious": malicious,
            "malicious_count": malicious_count,
            "harmless_count": harmless_count,
            "suspicious_count": suspicious_count,
            "country": country,
            "asn": asn,
            "asn_org": asn_org,
            "tags": list(set(all_tags)) if all_tags else None,
        }

    def _build_response(self, entry: ThreatIntel, provider_results: list[ThreatProviderResult], cached: bool = False) -> dict[str, Any]:
        return {
            "id": entry.id,
            "ioc_type": entry.ioc_type,
            "ioc_value": entry.ioc_value,
            "normalized_value": entry.normalized_value,
            "reputation_score": entry.reputation_score,
            "confidence": entry.confidence,
            "is_malicious": entry.is_malicious,
            "malicious_count": entry.malicious_count,
            "harmless_count": entry.harmless_count,
            "suspicious_count": entry.suspicious_count,
            "country": entry.country,
            "asn": entry.asn,
            "asn_org": entry.asn_org,
            "tags": entry.tags,
            "first_seen": entry.first_seen.isoformat() if entry.first_seen else None,
            "last_seen": entry.last_seen.isoformat() if entry.last_seen else None,
            "last_analysis": entry.last_analysis.isoformat() if entry.last_analysis else None,
            "cached": cached,
            "providers": [
                {
                    "name": pr.provider,
                    "reputation": pr.reputation,
                    "confidence": pr.confidence,
                    "malicious": pr.malicious,
                    "categories": pr.categories,
                    "looked_up_at": pr.looked_up_at.isoformat(),
                }
                for pr in provider_results
            ],
        }

    async def list_intel(
        self, page: int = 1, page_size: int = 20,
        sort_by: str = "last_analysis", sort_order: str = "desc",
        filters: dict[str, Any] | None = None,
        db: AsyncSession | None = None,
    ) -> tuple[list[ThreatIntel], int]:
        async with async_session_factory() as session:
            query = select(ThreatIntel)
            if filters:
                if filters.get("ioc_type"):
                    query = query.where(ThreatIntel.ioc_type == filters["ioc_type"])
                if filters.get("is_malicious") is not None:
                    query = query.where(ThreatIntel.is_malicious == filters["is_malicious"])
                if filters.get("q"):
                    query = query.where(ThreatIntel.normalized_value.ilike(f"%{filters['q']}%"))
            count_q = select(func.count()).select_from(query.subquery())
            total = (await session.execute(count_q)).scalar() or 0
            sort_col = getattr(ThreatIntel, sort_by, ThreatIntel.last_analysis)
            order_fn = desc if sort_order == "desc" else asc
            query = query.order_by(order_fn(sort_col)).offset((page - 1) * page_size).limit(page_size)
            result = await session.execute(query)
            items = list(result.scalars().all())
            return items, total

    async def get_stats(self, db: AsyncSession | None = None) -> dict[str, Any]:
        async with async_session_factory() as session:
            total = (await session.execute(select(func.count(ThreatIntel.id)))).scalar() or 0
            malicious = (await session.execute(
                select(func.count(ThreatIntel.id)).where(ThreatIntel.is_malicious == True)
            )).scalar() or 0
            by_type_q = await session.execute(
                select(ThreatIntel.ioc_type, func.count(ThreatIntel.id)).group_by(ThreatIntel.ioc_type)
            )
            by_type = dict(by_type_q.all())
            providers_q = await session.execute(
                select(ThreatProviderResult.provider, func.count(ThreatProviderResult.id))
                .group_by(ThreatProviderResult.provider)
            )
            provider_stats = dict(providers_q.all())
            recent = await session.execute(
                select(ThreatIntel).order_by(ThreatIntel.last_analysis.desc()).limit(5)
            )
            recent_items = [
                {"id": r.id, "ioc_type": r.ioc_type, "ioc_value": r.ioc_value,
                 "is_malicious": r.is_malicious, "reputation_score": r.reputation_score}
                for r in recent.scalars().all()
            ]
            return {
                "total_iocs": total,
                "malicious_count": malicious,
                "harmless_count": total - malicious,
                "by_type": by_type,
                "provider_stats": provider_stats,
                "recent_lookups": recent_items,
            }

