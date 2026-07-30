from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.soar import Playbook, PlaybookExecution
from app.soar.executor import execute_playbook


async def schedule_playbook(
    db: AsyncSession,
    playbook_id: str,
    trigger_event: str,
    incident_id: str | None = None,
    delay_ms: int = 0,
    config: dict[str, Any] | None = None,
) -> PlaybookExecution | None:
    result = await db.execute(select(Playbook).where(Playbook.id == playbook_id, Playbook.is_active == True))
    playbook = result.scalar_one_or_none()
    if not playbook:
        return None
    return await execute_playbook(
        db,
        playbook_id=playbook_id,
        incident_id=incident_id,
        triggered_by=f"scheduler:{trigger_event}",
        context={"trigger_event": trigger_event, "scheduled": True, **(config or {})},
    )


async def check_auto_triggers(db: AsyncSession, incident: Any) -> list[PlaybookExecution]:
    severity = getattr(incident, "severity", "")
    category = getattr(incident, "category", "")

    type_map = {
        "ssh_brute_force": ["ssh", "brute", "brute_force"],
        "windows_malware": ["malware", "windows"],
        "credential_stuffing": ["credential", "stuffing"],
        "ransomware": ["ransomware", "ransom"],
        "sql_injection": ["sql", "sqli", "injection"],
        "xss": ["xss", "cross_site"],
        "port_scan": ["port_scan", "scanning"],
        "privilege_escalation": ["privilege", "escalation"],
        "impossible_travel": ["impossible", "travel"],
        "insider_threat": ["insider"],
        "data_exfiltration": ["exfiltration", "data_exfil"],
        "suspicious_powershell": ["powershell"],
        "beaconing": ["beacon", "c2"],
        "lateral_movement": ["lateral", "movement"],
    }

    triggered = []
    if severity in ("critical", "high"):
        category_lower = (category or "").lower()
        for ptype, keywords in type_map.items():
            if any(kw in category_lower for kw in keywords):
                result = await db.execute(
                    select(Playbook).where(
                        Playbook.playbook_type == ptype,
                        Playbook.is_active == True,
                    )
                )
                playbook = result.scalar_one_or_none()
                if playbook:
                    execution = await execute_playbook(
                        db,
                        playbook_id=playbook.id,
                        incident_id=incident.id,
                        triggered_by="auto_trigger",
                        context={"alert_ids": getattr(incident, "alert_ids", []), "asset_ids": getattr(incident, "asset_ids", [])},
                    )
                    triggered.append(execution)
    return triggered
