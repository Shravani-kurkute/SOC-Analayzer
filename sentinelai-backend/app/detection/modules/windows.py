from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult


class WindowsDetectionModule(BaseDetectionModule):
    name = "windows"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "WIN-001":
            return self._privilege_escalation(rule, matching)
        return None

    def _privilege_escalation(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        for e in events:
            action = (e.get("action") or "").lower()
            source = (e.get("source") or "").lower()
            if "service" in action or "registry" in action or "schtask" in action:
                username = e.get("username", "unknown")
                return self._build_result(
                    rule, e,
                    title=f"Windows Privilege Escalation by {username}",
                    description=f"User {username} performed a privileged operation ({action}) on {source} at {e.get('timestamp', '')}. Possible service installation or registry modification.",
                    source_ip=e.get("src_ip") or e.get("source_ip"),
                    severity="critical",
                    score=85,
                    tags=["windows", "privilege-escalation", "service", "T1543"],
                    raw_data=e,
                )
        return None
