from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.detection import DetectionResult


class BaseDetectionModule:
    name: str = "base"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        raise NotImplementedError

    def _build_result(
        self, rule: dict[str, Any], event: dict[str, Any] | None = None, **overrides: Any
    ) -> DetectionResult:
        mitre = rule.get("mitre_mapping", {})
        return DetectionResult(
            title=overrides.get("title", rule["name"]),
            description=overrides.get("description", rule.get("description")),
            severity=overrides.get("severity", rule["severity"]),
            source=overrides.get("source"),
            source_ip=overrides.get("source_ip"),
            destination_ip=overrides.get("destination_ip"),
            source_port=overrides.get("source_port"),
            destination_port=overrides.get("destination_port"),
            protocol=overrides.get("protocol"),
            mitre_technique_id=overrides.get("mitre_technique_id", mitre.get("technique_id")),
            mitre_tactic=overrides.get("mitre_tactic", mitre.get("tactic")),
            rule_id=overrides.get("rule_id", rule["id"]),
            rule_name=overrides.get("rule_name", rule["name"]),
            score=overrides.get("score", int(rule.get("risk_score", 5) * 10)),
            raw_data=overrides.get("raw_data"),
            tags=overrides.get("tags", []),
            asset_ids=overrides.get("asset_ids"),
            country=overrides.get("country"),
            city=overrides.get("city"),
            correlation_group_id=overrides.get("correlation_group_id"),
            recommendation=overrides.get("recommendation", rule.get("recommendation")),
        )

    def _find_events(
        self, events: list[dict[str, Any]], conditions: dict[str, Any]
    ) -> list[dict[str, Any]]:
        matching = list(events)
        sources = conditions.get("sources", [])
        if sources:
            matching = [e for e in matching if any(s.lower() in str(e.get("source", "")).lower() for s in sources)]
        actions = conditions.get("actions", [])
        if actions:
            matching = [e for e in matching if any(a.lower() in str(e.get("action", "")).lower() or a.lower() in str(e.get("raw", {})).lower() for a in actions)]
        return matching
