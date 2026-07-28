import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult


SQLI_PATTERNS = [
    r"\bSELECT\b.*\bFROM\b", r"\bUNION\b.*\bSELECT\b",
    r"\bOR\s+1\s*=\s*1\b", r"\bOR\s+'1'\s*=\s*'1'\b",
    r"\bDROP\s+TABLE\b", r"\bINSERT\s+INTO\b",
    r"\bDELETE\s+FROM\b", r"\bUPDATE\s+.*\bSET\b",
    r"--\s*$", r"';.*--", r"\bxp_cmdshell\b",
    r"\bWAITFOR\s+DELAY\b", r"\bbenchmark\s*\(",
    r"'\s*OR\s*'\d'\s*=\s*'\d", r"1=1", r"' OR '1'='1",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>", r"javascript:",
    r"onerror\s*=", r"onload\s*=", r"onclick\s*=",
    r"alert\s*\(", r"<img[^>]*>.*?</img>",
    r"<svg[^>]*>", r"<iframe[^>]*>",
    r"prompt\s*\(", r"confirm\s*\(",
]

RCE_PATTERNS = [
    r";\s*(ls|cat|whoami|id|pwd|uname|wget|curl|nc|bash|sh|python|perl|ruby)\b",
    r"\$\s*\((.*)\)", r"`.*`",
    r"system\s*\(.*\)", r"exec\s*\(.*\)",
    r"shell_exec\s*\(", r"passthru\s*\(",
    r"/etc/passwd", r"\.\./\.\./", r"\.\.\\\.\.\\",
]

PT_PATTERNS = [
    r"\.\./", r"\.\.\\", r"\.\.%2f", r"\.\.%5c",
    r"/etc/passwd", r"/etc/shadow", r"/windows/win\.ini",
    r"boot\.ini", r"web\.config", r"\.git/config",
]


class WebDetectionModule(BaseDetectionModule):
    name = "web"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "WEB-001":
            return self._sql_injection(rule, matching)
        elif rule_id == "WEB-002":
            return self._xss(rule, matching)
        elif rule_id == "WEB-003":
            return self._rce(rule, matching)
        elif rule_id == "WEB-004":
            return self._path_traversal(rule, matching)
        return None

    def _match_patterns(
        self, rule: dict[str, Any], events: list[dict[str, Any]], patterns: list[str],
        attack_type: str, mitre_id: str, severity: str, score: int, tags: list[str]
    ) -> DetectionResult | None:
        for e in events:
            raw = e.get("raw", {})
            if isinstance(raw, str):
                text = raw.lower()
            else:
                text = str(raw).lower()
            url = str(e.get("raw", {})).lower() if isinstance(e.get("raw"), str) else ""
            full_text = text + " " + url + " " + str(e.get("action", "")).lower() + " " + str(e.get("source", "")).lower()
            for pat in patterns:
                if re.search(pat, full_text, re.IGNORECASE):
                    return self._build_result(
                        rule, e,
                        title=f"{attack_type} from {e.get('src_ip', 'unknown')}",
                        description=f"{attack_type} pattern detected in request from {e.get('src_ip', 'unknown')} targeting {e.get('dest_ip', 'unknown')} at {e.get('timestamp', '')}",
                        source_ip=e.get("src_ip") or e.get("source_ip"),
                        destination_ip=e.get("dest_ip") or e.get("destination_ip"),
                        destination_port=e.get("dest_port") or e.get("destination_port"),
                        severity=severity,
                        score=score,
                        tags=tags + [mitre_id],
                        raw_data=e,
                    )
        return None

    def _sql_injection(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        return self._match_patterns(rule, events, SQLI_PATTERNS, "SQL Injection", "T1190", "critical", 90, ["web", "sql-injection", "initial-access"])

    def _xss(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        return self._match_patterns(rule, events, XSS_PATTERNS, "XSS Attack", "T1059.007", "high", 75, ["web", "xss", "execution"])

    def _rce(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        return self._match_patterns(rule, events, RCE_PATTERNS, "RCE Attempt", "T1203", "critical", 95, ["web", "rce", "execution"])

    def _path_traversal(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        return self._match_patterns(rule, events, PT_PATTERNS, "Path Traversal", "T1005", "high", 70, ["web", "path-traversal", "collection"])
