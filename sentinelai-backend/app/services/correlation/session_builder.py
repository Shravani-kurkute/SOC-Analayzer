from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.services.correlation.rules import CorrelationRule


class SessionBuilder:
    def __init__(self, rule: CorrelationRule):
        self.rule = rule
        self.correlation_id = str(uuid4())

    def build_session(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not events:
            raise ValueError("Cannot build session from empty events list")

        sorted_events = sorted(events, key=lambda e: e.get("timestamp", datetime.now(timezone.utc)))
        first = sorted_events[0]
        last = sorted_events[-1]

        source_ip = self._resolve_field(first, "source_ip")
        dest_ip = self._resolve_field(first, "destination_ip")
        username = self._resolve_field(first, "username")
        hostname = self._resolve_field(first, "hostname")
        session_id = self._resolve_field(first, "session_id")

        attack_chain = self.rule.metadata.get("attack_chain", [])
        risk_score = self._calculate_risk(sorted_events)
        event_count = len(sorted_events)

        return {
            "correlation_id": self.correlation_id,
            "group_type": self.rule.group_type,
            "source_ip": source_ip,
            "destination_ip": dest_ip,
            "username": username,
            "hostname": hostname,
            "session_id": session_id,
            "start_time": first.get("timestamp", datetime.now(timezone.utc)),
            "end_time": last.get("timestamp", datetime.now(timezone.utc)),
            "event_count": event_count,
            "risk_score": risk_score,
            "status": "open" if risk_score >= 3.0 else "monitoring",
            "attack_chain": attack_chain,
            "description": self._build_description(rule_name=self.rule.name, source_ip=source_ip, username=username, event_count=event_count, group_type=self.rule.group_type),
        }

    def build_event_entry(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "parsed_event_id": event.get("id"),
            "log_entry_id": event.get("log_entry_id"),
            "event_type": event.get("event_type", "unknown"),
            "event_source": event.get("event_source"),
            "source_ip": event.get("source_ip"),
            "destination_ip": event.get("destination_ip"),
            "username": event.get("username"),
            "timestamp": event.get("timestamp", datetime.now(timezone.utc)),
            "action": event.get("action"),
            "severity": event.get("severity"),
            "risk_score": event.get("risk_score"),
            "raw_message": event.get("raw_message"),
            "metadata": event.get("metadata"),
        }

    def _calculate_risk(self, events: list[dict[str, Any]]) -> float:
        weights = self.rule.risk_weights
        if not weights:
            return min(len(events) * 1.0, 10.0)

        base_score = 0.0
        for event in events:
            action = event.get("action", "")
            score = event.get("risk_score", 0) or 0
            base_score += score
            for key, weight in weights.items():
                if key in action.lower():
                    base_score += weight * 5.0

        severity_map = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0, "info": 0.5}
        for event in events:
            sev = event.get("severity", "").lower()
            if sev in severity_map:
                base_score += severity_map[sev]

        return round(min(base_score, 10.0), 2)

    def _resolve_field(self, event: dict[str, Any], field: str) -> str | None:
        val = event.get(field)
        return str(val) if val is not None else None

    def _build_description(self, **kwargs: Any) -> str:
        templates = {
            "ssh_session": "SSH session correlation from {source_ip} — {event_count} events, {attack_chain}",
            "port_scan": "Port scan detected from {source_ip} — {event_count} ports scanned",
            "firewall_block": "Firewall blocks from {source_ip} — {event_count} blocked attempts",
            "web_attack": "Web attack pattern from {source_ip} — {event_count} events",
            "web_error_chain": "Web error chain from {source_ip} — {event_count} events",
            "attack_chain": "Multi-stage attack chain — {event_count} events, user {username}",
            "credential_stuffing": "Credential stuffing from {source_ip} — {event_count} attempts",
            "credential_compromise": "Credential anomaly for user {username} — {event_count} locations",
            "targeted_attack": "Targeted attack on {hostname} — {event_count} events",
        }
        template = templates.get(kwargs.get("group_type", ""), "Correlated {group_type} — {event_count} events")
        return template.format(**kwargs)
