from datetime import datetime
from typing import Any


class TimelineBuilder:
    def build_timeline(
        self,
        group: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        sorted_events = sorted(events, key=lambda e: e.get("timestamp", datetime.min))

        timeline: list[dict[str, Any]] = []
        for i, event in enumerate(sorted_events):
            timeline.append({
                "sequence": i + 1,
                "timestamp": event.get("timestamp"),
                "event_id": event.get("id"),
                "event_type": event.get("event_type", "unknown"),
                "action": event.get("action"),
                "source_ip": event.get("source_ip"),
                "destination_ip": event.get("destination_ip"),
                "username": event.get("username"),
                "severity": event.get("severity"),
                "risk_score": event.get("risk_score"),
                "raw_message": event.get("raw_message", "")[:200],
                "phase": self._classify_phase(event, group),
            })

        return timeline

    def build_attack_chain(
        self,
        timeline: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not timeline:
            return []

        phases: dict[str, list[dict[str, Any]]] = {}
        for entry in timeline:
            phase = entry["phase"] or "unknown"
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(entry)

        chain = []
        phase_order = [
            "reconnaissance", "initial_access", "execution",
            "persistence", "privilege_escalation", "defense_evasion",
            "credential_access", "discovery", "lateral_movement",
            "collection", "command_and_control", "exfiltration",
            "impact", "unknown",
        ]
        for phase_name in phase_order:
            if phase_name in phases:
                chain.append({
                    "phase": phase_name,
                    "events": phases[phase_name],
                    "count": len(phases[phase_name]),
                    "max_severity": self._max_severity(phases[phase_name]),
                })

        return chain

    def build_event_tree(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tree: dict[str, Any] = {
            "source_groups": {},
            "total_events": len(events),
        }

        for event in events:
            src = event.get("source_ip", "unknown")
            if src not in tree["source_groups"]:
                tree["source_groups"][src] = {"events": [], "count": 0}
            tree["source_groups"][src]["events"].append(event)
            tree["source_groups"][src]["count"] += 1

        for src in tree["source_groups"]:
            grp = tree["source_groups"][src]
            grp["action_types"] = self._count_actions(grp["events"])
            grp["severity_distribution"] = self._severity_distribution(grp["events"])
            grp["time_span"] = self._time_span(grp["events"])

        return tree

    def _classify_phase(self, event: dict[str, Any], group: dict[str, Any]) -> str | None:
        chain = group.get("attack_chain", [])
        if not chain:
            return None

        action = (event.get("action") or "").lower()
        event_type = (event.get("event_type") or "").lower()

        mapping: dict[str, str] = {
            "failed_password": "credential_access",
            "accepted": "initial_access",
            "deny": "defense_evasion",
            "block": "defense_evasion",
            "sql_injection": "initial_access",
            "path_traversal": "initial_access",
            "command_execution": "execution",
            "xss": "initial_access",
            "scan": "reconnaissance",
            "connect": "reconnaissance",
            "login": "credential_access",
            "sudo": "privilege_escalation",
            "error": "initial_access",
        }

        for key, phase in mapping.items():
            if key in action or key in event_type:
                return phase

        return chain[0] if chain else None

    def _count_actions(self, events: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in events:
            action = e.get("action", "unknown")
            counts[action] = counts.get(action, 0) + 1
        return counts

    def _severity_distribution(self, events: list[dict[str, Any]]) -> dict[str, int]:
        dist: dict[str, int] = {}
        for e in events:
            sev = e.get("severity", "info")
            dist[sev] = dist.get(sev, 0) + 1
        return dist

    def _time_span(self, events: list[dict[str, Any]]) -> dict[str, str | None]:
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
        if not timestamps:
            return {"start": None, "end": None}
        return {"start": str(min(timestamps)), "end": str(max(timestamps))}

    def _max_severity(self, events: list[dict[str, Any]]) -> str:
        order = ["info", "low", "medium", "high", "critical"]
        max_idx = 0
        for e in events:
            sev = e.get("severity", "info")
            idx = order.index(sev) if sev in order else 0
            max_idx = max(max_idx, idx)
        return order[max_idx]
