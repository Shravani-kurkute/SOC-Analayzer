from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult


class LinuxDetectionModule(BaseDetectionModule):
    name = "linux"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "LIN-001":
            return self._sudo_escalation(rule, matching)
        elif rule_id == "LIN-002":
            return self._cron_persistence(rule, matching)
        return None

    def _sudo_escalation(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        for e in events:
            action = (e.get("action") or "").lower()
            if "sudo" in action or "su " in action:
                username = e.get("username", "unknown")
                return self._build_result(
                    rule, e,
                    title=f"Sudo/SU Privilege Escalation by {username}",
                    description=f"User {username} used privilege escalation command ({action}) on {e.get('source', 'unknown')} at {e.get('timestamp', '')}",
                    source_ip=e.get("src_ip") or e.get("source_ip"),
                    severity="high",
                    score=80,
                    tags=["linux", "privilege-escalation", "sudo", "T1068"],
                    raw_data=e,
                )
        return None

    def _cron_persistence(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        for e in events:
            action = (e.get("action") or "").lower()
            if "cron" in action or "crontab" in action:
                return self._build_result(
                    rule, e,
                    title="Suspicious Cron Modification Detected",
                    description=f"Cron job modification detected on {e.get('source', 'unknown')} at {e.get('timestamp', '')} by user {e.get('username', 'unknown')}. Verify if legitimate.",
                    source_ip=e.get("src_ip") or e.get("source_ip"),
                    severity="high",
                    score=75,
                    tags=["linux", "persistence", "cron", "T1053.003"],
                    raw_data=e,
                )
        return None
