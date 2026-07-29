from __future__ import annotations

import json as json_module
import time
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import get_provider
from app.ai.prompt_builder import build_investigation_prompt
from app.ai.report_builder import parse_ai_response
from app.ai.timeline_builder import build_timeline
from app.core.config import settings
from app.models.ai_investigation import AIInvestigation
from app.models.alert import Alert
from app.models.correlation_event import CorrelationEvent
from app.models.correlation_group import CorrelationGroup
from app.models.incident import Incident
from app.models.ioc_entry import IocEntry
from app.models.mitre_technique import MitreTechnique
from app.models.threat_intel import ThreatIntel

logger = structlog.get_logger(__name__)


class AIInvestigationService:

    async def investigate(
        self,
        incident_id: str,
        db: AsyncSession,
        provider_name: str | None = None,
    ) -> dict[str, Any]:
        incident = await self._get_incident(incident_id, db)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        alerts = await self._get_alerts(incident.alert_ids or [], db)
        iocs = await self._get_iocs(incident_id, alerts, db)
        threat_intel = await self._get_threat_intel(iocs, db)
        mitre_techniques = await self._get_mitre_techniques(alerts, db)
        correlated_events = await self._get_correlated_events(alerts, db)
        timeline = build_timeline(alerts, correlated_events, iocs)

        existing = await self._get_existing(incident_id, db)
        if existing:
            prompt_parts = []
            if existing.prompt:
                prompt_parts.append(existing.prompt)

        prompt = build_investigation_prompt(
            incident=incident.to_dict(),
            alerts=[a.to_dict() for a in alerts],
            iocs=[i.to_dict() for i in iocs],
            threat_intel=[t.to_dict() for t in threat_intel],
            mitre_techniques=[m.to_dict() for m in mitre_techniques],
            correlated_events=[e.to_dict() for e in correlated_events],
            timeline=timeline,
        )

        provider = get_provider(provider_name)
        system_prompt = (
            "You are SentinelAI, an expert SOC analyst. "
            "Analyze the incident data provided and return ONLY valid JSON. "
            "Do not include any text outside the JSON response."
        )

        try:
            ai_response = await provider.generate(prompt, system_prompt)
            parsed = parse_ai_response(ai_response.text)

            investigation_data = {
                "incident_id": incident_id,
                "provider": provider_name or settings.AI_PROVIDER,
                "prompt": prompt,
                "response": ai_response.text,
                "summary": parsed.get("summary", ""),
                "attack_explanation": parsed.get("attack_explanation", ""),
                "timeline_data": timeline,
                "root_cause": parsed.get("root_cause", ""),
                "mitre_explanation": parsed.get("mitre_explanation", ""),
                "ioc_summary": parsed.get("ioc_summary", ""),
                "risk_explanation": parsed.get("risk_explanation", ""),
                "recommendations": parsed.get("recommendations", []),
                "containment": parsed.get("containment", ""),
                "recovery": parsed.get("recovery", ""),
                "hunting_queries": parsed.get("hunting_queries", []),
                "false_positive_probability": parsed.get("false_positive_probability"),
                "confidence_score": parsed.get("confidence_score"),
                "tokens_used": ai_response.tokens_used,
                "latency_ms": ai_response.latency_ms,
                "error": None,
            }

            if existing:
                for key, val in investigation_data.items():
                    setattr(existing, key, val)
                investigation = existing
            else:
                investigation = AIInvestigation(**investigation_data)
                db.add(investigation)

            await db.flush()
            await db.refresh(investigation)

        except Exception as e:
            logger.exception("AI investigation failed", incident_id=incident_id)
            error_data = {
                "incident_id": incident_id,
                "provider": provider_name or settings.AI_PROVIDER,
                "prompt": prompt,
                "response": None,
                "error": str(e),
            }
            if existing:
                for key, val in error_data.items():
                    setattr(existing, key, val)
                investigation = existing
            else:
                investigation = AIInvestigation(**error_data)
                db.add(investigation)
            await db.flush()
            await db.refresh(investigation)

        return self._to_dict(investigation)

    async def get_report(self, incident_id: str, db: AsyncSession) -> dict[str, Any] | None:
        result = await db.execute(
            select(AIInvestigation).where(
                AIInvestigation.incident_id == incident_id,
                AIInvestigation.error.is_(None),
            ).order_by(AIInvestigation.created_at.desc()).limit(1)
        )
        inv = result.scalar_one_or_none()
        return self._to_dict(inv) if inv else None

    async def list_history(self, db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[dict[str, Any]], int]:
        total = await db.scalar(select(func.count(AIInvestigation.id)))
        result = await db.execute(
            select(AIInvestigation)
            .order_by(AIInvestigation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()
        return [self._to_list_item(i) for i in items], total or 0

    async def delete_history(self, investigation_id: str, db: AsyncSession) -> bool:
        result = await db.execute(select(AIInvestigation).where(AIInvestigation.id == investigation_id))
        inv = result.scalar_one_or_none()
        if not inv:
            return False
        await db.delete(inv)
        return True

    async def get_stats(self, db: AsyncSession) -> dict[str, Any]:
        total = await db.scalar(select(func.count(AIInvestigation.id))) or 0

        avg_confidence = await db.scalar(
            select(func.avg(AIInvestigation.confidence_score))
            .where(AIInvestigation.confidence_score.isnot(None))
        ) or 0.0

        avg_latency = await db.scalar(
            select(func.avg(AIInvestigation.latency_ms))
            .where(AIInvestigation.latency_ms.isnot(None))
        ) or 0.0

        provider_result = await db.execute(
            select(AIInvestigation.provider, func.count(AIInvestigation.id))
            .group_by(AIInvestigation.provider)
        )
        provider_usage = {row[0]: row[1] for row in provider_result}

        recent = await db.execute(
            select(AIInvestigation)
            .order_by(AIInvestigation.created_at.desc())
            .limit(5)
        )
        recent_items = recent.scalars().all()

        recent_list = []
        for inv in recent_items:
            incident_title = None
            if inv.incident_id:
                inc_result = await db.execute(select(Incident).where(Incident.id == inv.incident_id))
                inc = inc_result.scalar_one_or_none()
                if inc:
                    incident_title = inc.title
            recent_list.append(self._to_list_item(inv, incident_title))

        return {
            "total_investigations": total,
            "average_confidence": round(float(avg_confidence), 4),
            "average_latency_ms": round(float(avg_latency), 2),
            "provider_usage": provider_usage,
            "recent_investigations": recent_list,
        }

    async def _get_incident(self, incident_id: str, db: AsyncSession) -> Incident | None:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        return result.scalar_one_or_none()

    async def _get_alerts(self, alert_ids: list[str], db: AsyncSession) -> list[Alert]:
        if not alert_ids:
            return []
        result = await db.execute(select(Alert).where(Alert.id.in_(alert_ids)))
        return list(result.scalars().all())

    async def _get_iocs(self, incident_id: str, alerts: list[dict], db: AsyncSession) -> list:
        source_ids = [incident_id] + [a.get("id", "") for a in alerts]
        source_ids = [s for s in source_ids if s]
        result = await db.execute(
            select(IocEntry).where(
                IocEntry.source_ids.overlap(source_ids) if source_ids else False
            )
        )
        return list(result.scalars().all())

    async def _get_threat_intel(self, iocs: list, db: AsyncSession) -> list:
        if not iocs:
            return []
        values = [i.normalized_value for i in iocs if hasattr(i, "normalized_value") and i.normalized_value]
        if not values:
            return []
        result = await db.execute(
            select(ThreatIntel).where(ThreatIntel.normalized_value.in_(values))
        )
        return list(result.scalars().all())

    async def _get_mitre_techniques(self, alerts: list[dict], db: AsyncSession) -> list:
        mitre_ids = set()
        for a in alerts:
            tid = a.get("mitre_technique_id")
            if tid:
                mitre_ids.add(tid)
        if not mitre_ids:
            return []
        result = await db.execute(
            select(MitreTechnique).where(MitreTechnique.technique_id.in_(mitre_ids))
        )
        return list(result.scalars().all())

    async def _get_correlated_events(self, alerts: list[dict], db: AsyncSession) -> list:
        group_ids = set()
        for a in alerts:
            gid = a.get("correlation_group_id")
            if gid:
                group_ids.add(gid)
        if not group_ids:
            return []
        result = await db.execute(
            select(CorrelationEvent).where(CorrelationEvent.group_id.in_(list(group_ids)))
        )
        return list(result.scalars().all())

    async def _get_existing(self, incident_id: str, db: AsyncSession) -> AIInvestigation | None:
        result = await db.execute(
            select(AIInvestigation).where(AIInvestigation.incident_id == incident_id)
        )
        return result.scalar_one_or_none()

    def _to_dict(self, inv: AIInvestigation) -> dict[str, Any]:
        return {
            "id": inv.id,
            "incident_id": inv.incident_id,
            "provider": inv.provider,
            "prompt": inv.prompt,
            "summary": inv.summary,
            "attack_explanation": inv.attack_explanation,
            "timeline_data": inv.timeline_data or [],
            "root_cause": inv.root_cause,
            "mitre_explanation": inv.mitre_explanation,
            "ioc_summary": inv.ioc_summary,
            "risk_explanation": inv.risk_explanation,
            "recommendations": inv.recommendations or [],
            "containment": inv.containment,
            "recovery": inv.recovery,
            "hunting_queries": inv.hunting_queries or [],
            "false_positive_probability": inv.false_positive_probability,
            "confidence_score": inv.confidence_score,
            "tokens_used": inv.tokens_used,
            "latency_ms": inv.latency_ms,
            "error": inv.error,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        }

    def _to_list_item(self, inv: AIInvestigation, incident_title: str | None = None) -> dict[str, Any]:
        return {
            "id": inv.id,
            "incident_id": inv.incident_id,
            "incident_title": incident_title,
            "provider": inv.provider,
            "summary": inv.summary,
            "confidence_score": inv.confidence_score,
            "tokens_used": inv.tokens_used,
            "latency_ms": inv.latency_ms,
            "error": inv.error,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        }
