import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules.auth import AuthDetectionModule
from app.detection.modules.firewall import FirewallDetectionModule
from app.detection.modules.linux import LinuxDetectionModule
from app.detection.modules.network import NetworkDetectionModule
from app.detection.modules.ssh import SSHDetectionModule
from app.detection.modules.web import WebDetectionModule
from app.detection.modules.windows import WindowsDetectionModule
from app.detection.registry import DetectionRuleRegistry
from app.detection.rules import register_all
from app.models.alert import Alert as AlertModel
from app.schemas.detection import DetectionResult

logger = logging.getLogger(__name__)


class DetectionEngine:
    def __init__(self) -> None:
        self.modules: dict[str, Any] = {}
        self._register_modules()

    def _register_modules(self) -> None:
        register_all()
        module_classes = [
            SSHDetectionModule,
            AuthDetectionModule,
            NetworkDetectionModule,
            FirewallDetectionModule,
            WebDetectionModule,
            LinuxDetectionModule,
            WindowsDetectionModule,
        ]
        for cls in module_classes:
            mod = cls()
            self.modules[mod.name] = mod

    async def run_rule(
        self, rule_id: str, events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        rule = DetectionRuleRegistry.get(rule_id)
        if not rule or not rule.get("enabled", True):
            return None
        category = rule.get("category", "")
        module = self.modules.get(category)
        if module:
            return await module.analyze(rule, events, db_session)
        return None

    async def run_all_rules(
        self, events: list[dict[str, Any]], db_session: AsyncSession
    ) -> list[DetectionResult]:
        results: list[DetectionResult] = []
        for rule in DetectionRuleRegistry.get_enabled():
            category = rule.get("category", "")
            module = self.modules.get(category)
            if not module:
                continue
            try:
                result = await module.analyze(rule, events, db_session)
                if result:
                    results.append(result)
            except Exception:
                logger.exception("Error running rule %s", rule.get("id"))
                continue
        return results

    def _create_alert_from_result(self, r: DetectionResult, db_session: AsyncSession) -> AlertModel:
        alert = AlertModel(
            title=r.title,
            description=r.description,
            severity=r.severity,
            status="open",
            source=r.source,
            source_ip=r.source_ip,
            destination_ip=r.destination_ip,
            source_port=r.source_port,
            destination_port=r.destination_port,
            protocol=r.protocol,
            mitre_technique_id=r.mitre_technique_id,
            mitre_tactic=r.mitre_tactic,
            rule_id=r.rule_id,
            rule_name=r.rule_name,
            score=r.score,
            raw_data=r.raw_data,
            enriched_data=r.enriched_data,
            tags=r.tags,
            asset_ids=r.asset_ids,
            country=r.country,
            city=r.city,
            correlation_group_id=r.correlation_group_id,
            recommendation=r.recommendation,
            created_by="system",
        )
        db_session.add(alert)
        return alert

    async def run_all_for_parsed(
        self, parsed_events: list[dict[str, Any]], db_session: AsyncSession
    ) -> list[AlertModel]:
        alerts: list[AlertModel] = []
        results = await self.run_all_rules(parsed_events, db_session)
        for r in results:
            alert = self._create_alert_from_result(r, db_session)
            alerts.append(alert)
        if results:
            try:
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise
        return alerts


engine = DetectionEngine()
