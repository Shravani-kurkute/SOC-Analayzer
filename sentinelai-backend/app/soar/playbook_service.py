from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.soar import Playbook
from app.schemas.soar import PlaybookCreate, PlaybookUpdate

PLAYBOOK_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "ssh_brute_force": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Analyst", "action": "notify_team", "config": {"severity": "high"}, "type": "action"},
        {"index": 3, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 4, "name": "Collect Logs", "action": "collect_logs", "config": {}, "type": "action"},
        {"index": 5, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 6, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "SSH brute force mitigated"}, "type": "action"},
    ],
    "windows_malware": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 2, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 3, "name": "Tag IOC", "action": "tag_ioc", "config": {"tag": "malware"}, "type": "action"},
        {"index": 4, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 5, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 6, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Malware contained"}, "type": "action"},
    ],
    "ransomware": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical", "title": "Ransomware Detected"}, "type": "action"},
        {"index": 3, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 4, "name": "Update Asset Risk", "action": "update_asset_risk", "config": {}, "type": "action"},
        {"index": 5, "name": "Tag IOC", "action": "tag_ioc", "config": {"tag": "ransomware"}, "type": "action"},
        {"index": 6, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 7, "name": "Export Evidence", "action": "export_evidence", "config": {}, "type": "action"},
        {"index": 8, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Ransomware incident resolved"}, "type": "action"},
    ],
    "credential_stuffing": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Team", "action": "notify_team", "config": {"severity": "high"}, "type": "action"},
        {"index": 3, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 4, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Credential stuffing mitigated"}, "type": "action"},
    ],
    "sql_injection": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 3, "name": "Notify Team", "action": "notify_team", "config": {"severity": "high"}, "type": "action"},
        {"index": 4, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "SQL injection blocked"}, "type": "action"},
    ],
    "xss": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Team", "action": "notify_team", "config": {"severity": "medium"}, "type": "action"},
        {"index": 3, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "XSS attack mitigated"}, "type": "action"},
    ],
    "port_scan": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Team", "action": "notify_team", "config": {"severity": "medium"}, "type": "action"},
        {"index": 3, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Port scan investigation complete"}, "type": "action"},
    ],
    "privilege_escalation": [
        {"index": 0, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 1, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 2, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 3, "name": "Update Asset Risk", "action": "update_asset_risk", "config": {}, "type": "action"},
        {"index": 4, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 5, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Privilege escalation contained"}, "type": "action"},
    ],
    "impossible_travel": [
        {"index": 0, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Notify Team", "action": "notify_team", "config": {"severity": "high"}, "type": "action"},
        {"index": 3, "name": "Update Asset Risk", "action": "update_asset_risk", "config": {}, "type": "action"},
        {"index": 4, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Impossible travel investigated"}, "type": "action"},
    ],
    "insider_threat": [
        {"index": 0, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Export Evidence", "action": "export_evidence", "config": {}, "type": "action"},
        {"index": 3, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 4, "name": "Create Ticket", "action": "create_ticket", "config": {"title": "Insider Threat Investigation"}, "type": "action"},
        {"index": 5, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 6, "name": "Close Incident", "action": "close_incident", "config": {}, "type": "action"},
    ],
    "data_exfiltration": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 2, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 3, "name": "Export Evidence", "action": "export_evidence", "config": {}, "type": "action"},
        {"index": 4, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 5, "name": "Update Threat Intel", "action": "update_threat_intel", "config": {"reputation_score": 80}, "type": "action"},
        {"index": 6, "name": "Generate Report", "action": "generate_report", "config": {"report_type": "incident"}, "type": "action"},
        {"index": 7, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Data exfiltration contained"}, "type": "action"},
    ],
    "suspicious_powershell": [
        {"index": 0, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 1, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 2, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 3, "name": "Collect Logs", "action": "collect_logs", "config": {}, "type": "action"},
        {"index": 4, "name": "Notify Team", "action": "notify_team", "config": {"severity": "high"}, "type": "action"},
        {"index": 5, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Suspicious PowerShell investigated"}, "type": "action"},
    ],
    "beaconing": [
        {"index": 0, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 1, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 2, "name": "Tag IOC", "action": "tag_ioc", "config": {"tag": "c2-beacon"}, "type": "action"},
        {"index": 3, "name": "Update Threat Intel", "action": "update_threat_intel", "config": {"reputation_score": 90}, "type": "action"},
        {"index": 4, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 5, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "C2 beacon blocked"}, "type": "action"},
    ],
    "lateral_movement": [
        {"index": 0, "name": "Disable User", "action": "disable_user", "config": {}, "type": "action"},
        {"index": 1, "name": "Block IP", "action": "block_ip", "config": {}, "type": "action"},
        {"index": 2, "name": "Run AI Investigation", "action": "run_ai_investigation", "config": {}, "type": "action"},
        {"index": 3, "name": "Update Asset Risk", "action": "update_asset_risk", "config": {}, "type": "action"},
        {"index": 4, "name": "Tag IOC", "action": "tag_ioc", "config": {"tag": "lateral-movement"}, "type": "action"},
        {"index": 5, "name": "Notify Team", "action": "notify_team", "config": {"severity": "critical"}, "type": "action"},
        {"index": 6, "name": "Close Incident", "action": "close_incident", "config": {"resolution": "Lateral movement contained"}, "type": "action"},
    ],
}


async def list_playbooks(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search: str | None = None,
    playbook_type: str | None = None,
    severity: str | None = None,
    is_template: bool | None = None,
) -> tuple[Sequence[Playbook], int]:
    query = select(Playbook)
    if search:
        query = query.where(Playbook.name.ilike(f"%{search}%"))
    if playbook_type:
        query = query.where(Playbook.playbook_type == playbook_type)
    if severity:
        query = query.where(Playbook.severity == severity)
    if is_template is not None:
        query = query.where(Playbook.is_template == is_template)
    sort_col = getattr(Playbook, sort_by, Playbook.created_at)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return result.scalars().all(), total


async def get_playbook(db: AsyncSession, playbook_id: str) -> Playbook | None:
    result = await db.execute(select(Playbook).where(Playbook.id == playbook_id))
    return result.scalar_one_or_none()


async def create_playbook(db: AsyncSession, data: PlaybookCreate, created_by: str | None = None) -> Playbook:
    pb = Playbook(
        name=data.name,
        description=data.description,
        playbook_type=data.playbook_type,
        severity=data.severity,
        category=data.category,
        tags=data.tags,
        is_template=data.is_template,
        steps=data.steps,
        config=data.config,
        created_by=created_by,
    )
    db.add(pb)
    await db.flush()
    await db.refresh(pb)
    return pb


async def create_from_template(db: AsyncSession, template_type: str, name: str | None = None, created_by: str | None = None) -> Playbook | None:
    steps = PLAYBOOK_TEMPLATES.get(template_type)
    if not steps:
        return None
    pb = Playbook(
        name=name or template_type.replace("_", " ").title(),
        playbook_type=template_type,
        severity="medium",
        is_template=False,
        steps=steps,
        created_by=created_by,
    )
    db.add(pb)
    await db.flush()
    await db.refresh(pb)
    return pb


async def update_playbook(db: AsyncSession, playbook_id: str, data: PlaybookUpdate) -> Playbook | None:
    pb = await get_playbook(db, playbook_id)
    if not pb:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pb, field, value)
    return pb


async def delete_playbook(db: AsyncSession, playbook_id: str) -> bool:
    pb = await get_playbook(db, playbook_id)
    if not pb:
        return False
    pb.is_active = False
    return True


async def get_playbook_stats(db: AsyncSession) -> dict[str, Any]:
    from app.models.soar import ApprovalRequest, PlaybookExecution
    from sqlalchemy import func as sf

    total = await db.scalar(sf.count(Playbook.id).where(Playbook.is_active == True)) or 0
    active = await db.scalar(sf.count(Playbook.id).where(Playbook.is_active == True)) or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    exec_today = await db.scalar(
        sf.count(PlaybookExecution.id).where(PlaybookExecution.created_at >= today_start)
    ) or 0
    total_execs = await db.scalar(sf.count(PlaybookExecution.id)) or 0

    avg_time = await db.scalar(sf.avg(PlaybookExecution.duration_ms)) or 0.0

    success_result = await db.execute(
        select(sf.count(PlaybookExecution.id)).where(PlaybookExecution.status == "completed")
    )
    success_count = success_result.scalar() or 0
    success_rate = (success_count / total_execs * 100) if total_execs > 0 else 0.0

    pending = await db.scalar(
        sf.count(ApprovalRequest.id).where(ApprovalRequest.status == "pending")
    ) or 0

    type_result = await db.execute(
        select(Playbook.playbook_type, sf.count(Playbook.id)).group_by(Playbook.playbook_type)
    )
    by_type = dict(type_result.all())

    sev_result = await db.execute(
        select(Playbook.severity, sf.count(Playbook.id)).group_by(Playbook.severity)
    )
    by_severity = dict(sev_result.all())

    recent = await db.execute(
        select(PlaybookExecution).order_by(PlaybookExecution.created_at.desc()).limit(5)
    )
    recent_execs = [{"id": e.id, "playbook_name": e.playbook_name, "status": e.status, "created_at": e.created_at.isoformat() if e.created_at else None} for e in recent.scalars().all()]

    return {
        "total_playbooks": total,
        "active_playbooks": active,
        "executions_today": exec_today,
        "total_executions": total_execs,
        "success_rate": success_rate,
        "avg_execution_time_ms": float(avg_time),
        "pending_approvals": pending,
        "by_type": by_type,
        "by_severity": by_severity,
        "recent_executions": recent_execs,
    }


def get_template_list() -> list[dict[str, Any]]:
    return [
        {"type": k, "steps": len(v), "name": k.replace("_", " ").title()}
        for k, v in PLAYBOOK_TEMPLATES.items()
    ]
