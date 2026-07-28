import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult

logger = logging.getLogger(__name__)


class AuthDetectionModule(BaseDetectionModule):
    name = "authentication"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "AUTH-001":
            return self._password_spray(rule, matching)
        elif rule_id == "AUTH-002":
            return self._credential_stuffing(rule, matching)
        elif rule_id == "AUTH-003":
            return self._impossible_travel(rule, matching)
        return None

    def _password_spray(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_users: dict[str, set[str]] = {}
        threshold = rule.get("threshold", {}).get("unique_users", 5)
        for e in events:
            action = (e.get("action") or "").lower()
            if "failed" in action or "fail" in action:
                src_ip = e.get("src_ip") or e.get("source_ip")
                username = e.get("username", "unknown")
                if src_ip:
                    ip_users.setdefault(src_ip, set()).add(username)
        for ip, users in ip_users.items():
            if len(users) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Password Spray Attack from {ip}",
                    description=f"Source {ip} attempted logins across {len(users)} unique usernames: {', '.join(list(users)[:15])}",
                    source_ip=ip,
                    severity="high",
                    score=70,
                    tags=["authentication", "password-spray", "T1110.003"],
                    raw_data={"ip": ip, "unique_users": list(users), "total_attempted": len(events)},
                )
        return None

    def _credential_stuffing(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_attempts: dict[str, list[dict[str, Any]]] = {}
        threshold = rule.get("threshold", {}).get("min_attempts", 15)
        for e in events:
            action = (e.get("action") or "").lower()
            if "failed" in action or "fail" in action:
                src_ip = e.get("src_ip") or e.get("source_ip")
                if src_ip:
                    ip_attempts.setdefault(src_ip, []).append(e)
        for ip, attempts in ip_attempts.items():
            if len(attempts) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Credential Stuffing from {ip}",
                    description=f"High volume of failed login attempts ({len(attempts)}) from {ip} in a short time window, indicating credential stuffing.",
                    source_ip=ip,
                    severity="critical",
                    score=85,
                    tags=["authentication", "credential-stuffing", "T1110.004"],
                    raw_data={"ip": ip, "total_attempts": len(attempts)},
                )
        return None

    def _impossible_travel(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        user_locations: dict[str, list[dict[str, Any]]] = {}
        for e in events:
            username = e.get("username", "")
            if not username:
                continue
            country = e.get("country") or e.get("city", "")
            if country:
                user_locations.setdefault(username, []).append(e)
        for username, locs in user_locations.items():
            if len(locs) >= 2:
                locs_sorted = sorted(locs, key=lambda x: x.get("timestamp", ""))
                for i in range(len(locs_sorted) - 1):
                    loc1 = locs_sorted[i]
                    loc2 = locs_sorted[i + 1]
                    t1 = loc1.get("country", "").lower()
                    t2 = loc2.get("country", "").lower()
                    if t1 and t2 and t1 != t2:
                        return self._build_result(
                            rule, loc2,
                            title=f"Impossible Travel for {username}",
                            description=f"User {username} accessed from {loc1.get('country', 'unknown')} and then {loc2.get('country', 'unknown')} within an impossibly short time.",
                            severity="critical",
                            score=95,
                            tags=["authentication", "impossible-travel", "account-compromise", "T1078"],
                            raw_data={"username": username, "locations": [{"country": loc1.get("country"), "time": loc1.get("timestamp")}, {"country": loc2.get("country"), "time": loc2.get("timestamp")}]},
                        )
        return None
