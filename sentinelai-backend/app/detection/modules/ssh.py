import logging
from typing import Any
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult

logger = logging.getLogger(__name__)


class SSHDetectionModule(BaseDetectionModule):
    name = "ssh"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "SSH-001":
            return self._ssh_brute_force(rule, matching)
        elif rule_id == "SSH-002":
            return self._ssh_brute_success(rule, matching)
        elif rule_id == "SSH-003":
            return self._ssh_root_login(rule, matching)
        return None

    def _ssh_brute_force(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_failures: dict[str, list[dict[str, Any]]] = {}
        threshold = rule.get("threshold", {}).get("failed_attempts", 5)
        for e in events:
            action = (e.get("action") or "").lower()
            src_ip = e.get("src_ip") or e.get("source_ip")
            if "failed" in action or "fail" in action or "invalid" in action:
                if src_ip:
                    ip_failures.setdefault(src_ip, []).append(e)
        for ip, ip_events in ip_failures.items():
            if len(ip_events) >= threshold:
                first_seen = ip_events[0].get("timestamp", "")
                last_seen = ip_events[-1].get("timestamp", "")
                usernames = list({e.get("username", "") for e in ip_events if e.get("username")})
                return self._build_result(
                    rule, ip_events[0],
                    title=f"SSH Brute Force from {ip}",
                    description=f"Detected {len(ip_events)} failed SSH login attempts from {ip} targeting {len(usernames)} usernames: {', '.join(usernames[:10])}",
                    source_ip=ip,
                    severity="high",
                    score=min(len(ip_events) * 15, 95),
                    tags=["ssh", "brute-force", "credential-access"] + (["multiple-users"] if len(usernames) > 1 else []),
                    raw_data={"events": [{"timestamp": e.get("timestamp"), "username": e.get("username"), "action": e.get("action")} for e in ip_events[:20]]},
                )
        return None

    def _ssh_brute_success(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_failures: dict[str, list[dict[str, Any]]] = {}
        ip_successes: dict[str, list[dict[str, Any]]] = {}
        threshold = rule.get("threshold", {}).get("failed_attempts", 3)
        for e in events:
            action = (e.get("action") or "").lower()
            src_ip = e.get("src_ip") or e.get("source_ip")
            if not src_ip:
                continue
            if "failed" in action or "fail" in action:
                ip_failures.setdefault(src_ip, []).append(e)
            elif "accepted" in action or "success" in action:
                ip_successes.setdefault(src_ip, []).append(e)
        for ip in ip_successes:
            if ip in ip_failures and len(ip_failures[ip]) >= threshold:
                return self._build_result(
                    rule, ip_successes[ip][0],
                    title=f"SSH Credential Compromise on {ip}",
                    description=f"Source {ip} had {len(ip_failures[ip])} failed attempts followed by successful login at {ip_successes[ip][0].get('timestamp', '')}",
                    source_ip=ip,
                    severity="critical",
                    score=95,
                    tags=["ssh", "credential-compromise", "initial-access", "T1078"],
                    raw_data={"failed_attempts": len(ip_failures[ip]), "successful": [{"timestamp": e.get("timestamp"), "username": e.get("username")} for e in ip_successes[ip]]},
                )
        return None

    def _ssh_root_login(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        for e in events:
            username = (e.get("username") or "").lower()
            action = (e.get("action") or "").lower()
            if username == "root" and ("accepted" in action or "success" in action):
                return self._build_result(
                    rule, e,
                    title="Direct SSH Root Login Detected",
                    description=f"Root logged into SSH from {e.get('src_ip', 'unknown')} at {e.get('timestamp', '')}",
                    source_ip=e.get("src_ip") or e.get("source_ip"),
                    severity="high",
                    score=80,
                    tags=["ssh", "root-login", "privilege-escalation", "best-practice-violation"],
                    raw_data=e,
                )
        return None
