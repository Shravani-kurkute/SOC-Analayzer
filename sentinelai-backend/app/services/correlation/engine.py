from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.correlation_event import CorrelationEvent as CorrelationEventModel
from app.models.correlation_group import CorrelationGroup as CorrelationGroupModel
from app.models.log_entry import LogEntry
from app.services.correlation.rules import CorrelationRule, CorrelationRuleRegistry
from app.services.correlation.session_builder import SessionBuilder
from app.services.correlation.timeline_builder import TimelineBuilder

logger = structlog.get_logger(__name__)


class CorrelationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_builder = TimelineBuilder()

    async def run_all_rules(self) -> dict[str, Any]:
        rules = CorrelationRuleRegistry.get_all()
        total_groups = 0
        total_events = 0

        for rule in rules:
            result = await self.run_rule(rule)
            total_groups += result["groups_created"]
            total_events += result["events_correlated"]

        return {
            "groups_created": total_groups,
            "events_correlated": total_events,
            "message": f"Correlation complete: {total_groups} groups, {total_events} events",
        }

    async def run_rule(self, rule: CorrelationRule) -> dict[str, Any]:
        events = await self._fetch_events_for_rule(rule)
        if not events:
            return {"groups_created": 0, "events_correlated": 0}

        grouped = self._group_events(events, rule)
        groups_created = 0
        events_correlated = 0

        for key, group_events in grouped.items():
            if len(group_events) < rule.min_events:
                continue

            if rule.require_sequence and rule.sequence_fields:
                if not self._check_sequence(group_events, rule.sequence_fields):
                    continue

            builder = SessionBuilder(rule)
            session_data = builder.build_session(group_events)
            db_group = await self._save_group(session_data)
            if not db_group:
                continue

            groups_created += 1
            for event in group_events:
                event_entry = builder.build_event_entry(event)
                await self._save_event(db_group.id, event_entry)
                events_correlated += 1

        await self.db.flush()
        return {"groups_created": groups_created, "events_correlated": events_correlated}

    async def _fetch_events_for_rule(self, rule: CorrelationRule) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - rule.time_window
        stmt = (
            select(LogEntry)
            .where(LogEntry.timestamp >= cutoff)
            .order_by(LogEntry.timestamp)
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()

        events = []
        for row in rows:
            events.append(self._log_entry_to_dict(row))
        return events

    def _group_events(self, events: list[dict[str, Any]], rule: CorrelationRule) -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for event in events:
            key_parts = []
            for field in rule.match_fields:
                val = event.get(field)
                if val:
                    key_parts.append(str(val))
            if not key_parts:
                continue
            key = "::".join(key_parts)

            groups[key].append(event)

        pruned: dict[str, list[dict[str, Any]]] = {}
        for key, grp in groups.items():
            sorted_grp = sorted(grp, key=lambda e: e.get("timestamp", datetime.min))
            pruned[key] = sorted_grp

        return pruned

    def _check_sequence(self, events: list[dict[str, Any]], sequence_fields: list[str]) -> bool:
        if len(events) < 2:
            return False

        for field in sequence_fields:
            values = [e.get(field) for e in events if e.get(field)]
            unique = set(str(v) for v in values if v)
            if len(unique) >= 2:
                return True
        return False

    async def _save_group(self, session_data: dict[str, Any]) -> CorrelationGroupModel | None:
        try:
            group = CorrelationGroupModel(
                correlation_id=session_data["correlation_id"],
                group_type=session_data["group_type"],
                source_ip=session_data.get("source_ip"),
                destination_ip=session_data.get("destination_ip"),
                username=session_data.get("username"),
                hostname=session_data.get("hostname"),
                session_id=session_data.get("session_id"),
                start_time=session_data["start_time"],
                end_time=session_data["end_time"],
                event_count=session_data["event_count"],
                risk_score=session_data["risk_score"],
                status=session_data["status"],
                attack_chain=session_data.get("attack_chain"),
                description=session_data.get("description"),
                extra_data=session_data.get("metadata"),
            )
            self.db.add(group)
            return group
        except Exception as e:
            logger.error("Failed to save correlation group", error=str(e))
            return None

    async def _save_event(self, group_id: str, event_data: dict[str, Any]) -> CorrelationEventModel | None:
        try:
            event = CorrelationEventModel(
                group_id=group_id,
                parsed_event_id=event_data.get("parsed_event_id"),
                log_entry_id=event_data.get("log_entry_id"),
                event_type=event_data["event_type"],
                event_source=event_data.get("event_source"),
                source_ip=event_data.get("source_ip"),
                destination_ip=event_data.get("destination_ip"),
                username=event_data.get("username"),
                timestamp=event_data["timestamp"],
                action=event_data.get("action"),
                severity=event_data.get("severity"),
                risk_score=event_data.get("risk_score"),
                raw_message=event_data.get("raw_message"),
                extra_data=event_data.get("metadata"),
            )
            self.db.add(event)
            return event
        except Exception as e:
            logger.error("Failed to save correlation event", error=str(e))
            return None

    def _log_entry_to_dict(self, entry: LogEntry) -> dict[str, Any]:
        return {
            "id": str(entry.id),
            "log_entry_id": str(entry.id),
            "event_type": self._detect_event_type(entry),
            "event_source": entry.log_source,
            "source_ip": entry.source_ip,
            "destination_ip": entry.destination_ip,
            "username": entry.user_id,
            "hostname": None,
            "session_id": None,
            "timestamp": entry.timestamp,
            "action": entry.action,
            "severity": self._classify_severity(entry),
            "risk_score": entry.threat_score or 0,
            "raw_message": entry.raw_message,
            "metadata": {"tags": entry.tags, "protocol": entry.protocol, "country": entry.country},
        }

    def _detect_event_type(self, entry: LogEntry) -> str:
        source = (entry.log_source or "").lower()
        action = (entry.action or "").lower()

        if "ssh" in source or "sshd" in source:
            return "ssh_login"
        if "apache" in source or "http" in source:
            return "web_access"
        if "nginx" in source:
            return "web_access"
        if "firewall" in source or "pfsense" in source or "cisco" in source or "fortinet" in source:
            return "firewall_event"
        if "linux" in source or "auth" in source or "syslog" in source:
            return "system_event"
        if "failed" in action or "denied" in action or "invalid" in action:
            return "security_event"
        return "unknown"

    def _classify_severity(self, entry: LogEntry) -> str:
        action = (entry.action or "").lower()
        score = entry.threat_score or 0

        if score >= 8:
            return "critical"
        if score >= 5:
            return "high"
        if score >= 3:
            return "medium"
        if score >= 1:
            return "low"

        high_severity_actions = ["failed", "denied", "reject", "block", "error", "attack", "malicious"]
        for ha in high_severity_actions:
            if ha in action:
                return "medium"

        return "info"
