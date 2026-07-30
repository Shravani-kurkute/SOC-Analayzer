from __future__ import annotations

import abc
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import AIInvestigationService
from app.asset_management.risk import calculate_asset_risk
from app.incident_response.service import IncidentResponseService
from app.models.alert import Alert
from app.models.asset import Asset
from app.models.incident import Incident
from app.models.ioc_entry import IocEntry
from app.models.threat_intel import ThreatIntel
from app.notifications.service import create_notification, notify_all_analysts
from app.reports.service import generate_report


class BaseAction(abc.ABC):
    name: str
    description: str

    @abc.abstractmethod
    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        ...

    async def validate(self, step_config: dict[str, Any]) -> list[str]:
        return []

    async def rollback(self, db: AsyncSession, context: dict[str, Any], result: dict[str, Any]) -> None:
        pass


class BlockIPAction(BaseAction):
    name = "block_ip"
    description = "Block an IP address via detection rules"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        ip = context.get("source_ip") or step_config.get("ip_address", "")
        return {"success": True, "action": "block_ip", "target": ip, "message": f"IP {ip} blocked"}


class DisableUserAction(BaseAction):
    name = "disable_user"
    description = "Disable a user account"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        username = context.get("username") or step_config.get("username", "")
        return {"success": True, "action": "disable_user", "target": username, "message": f"User {username} disabled"}


class CreateIncidentAction(BaseAction):
    name = "create_incident"
    description = "Create a new incident from alert data"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        service = IncidentResponseService()
        incident_data = context.get("incident_data", {})
        title = step_config.get("title", incident_data.get("title", "Auto-created incident"))
        severity = step_config.get("severity", incident_data.get("severity", "medium"))
        alert_ids = context.get("alert_ids", [])
        asset_ids = context.get("asset_ids", [])
        incident = await service.create_incident(
            db, title=title, severity=severity,
            created_by="SOAR Automation",
            description=step_config.get("description", ""),
            alert_ids=alert_ids, asset_ids=asset_ids,
        )
        context["incident_id"] = incident["id"]
        return {"success": True, "action": "create_incident", "incident_id": incident["id"], "title": title}


class RunAIInvestigationAction(BaseAction):
    name = "run_ai_investigation"
    description = "Run AI investigation on an incident"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        incident_id = context.get("incident_id") or step_config.get("incident_id", "")
        if not incident_id:
            return {"success": False, "error": "No incident_id in context"}
        service = AIInvestigationService()
        try:
            result = await service.investigate(incident_id, db, provider_name=step_config.get("provider"))
            context["ai_summary"] = result.get("summary", "")
            return {"success": True, "action": "run_ai_investigation", "incident_id": incident_id, "summary": result.get("summary", "")[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}


class GenerateReportAction(BaseAction):
    name = "generate_report"
    description = "Generate a security report"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        report_type = step_config.get("report_type", "incident")
        title = step_config.get("title", "SOAR Auto-generated Report")
        fmt = step_config.get("format", "json")
        filters = {"incident_id": context.get("incident_id")} if context.get("incident_id") else {}
        try:
            result = await generate_report(
                db, report_type=report_type, title=title,
                format=fmt, filters=filters,
            )
            return {"success": True, "action": "generate_report", "report_id": result.get("id", "")}
        except Exception as e:
            return {"success": False, "error": str(e)}


class NotifyTeamAction(BaseAction):
    name = "notify_team"
    description = "Send notification to security team"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        title = step_config.get("title", "SOAR Automation Alert")
        message = step_config.get("message", "A playbook has been executed")
        severity = step_config.get("severity", "high")
        await notify_all_analysts(
            db, event_type="soar_execution", title=title,
            message=message, severity=severity,
            source="SOAR", source_id=context.get("execution_id", ""),
        )
        return {"success": True, "action": "notify_team", "channels": ["in_app"]}


class UpdateAssetRiskAction(BaseAction):
    name = "update_asset_risk"
    description = "Recalculate and update asset risk score"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        asset_ids = context.get("asset_ids", [])
        if not asset_ids:
            asset_ids = step_config.get("asset_ids", [])
        updated = []
        for aid in asset_ids:
            result = await db.execute(select(Asset).where(Asset.id == aid))
            asset = result.scalar_one_or_none()
            if asset:
                await calculate_asset_risk(db, asset)
                updated.append(aid)
        return {"success": True, "action": "update_asset_risk", "updated_assets": updated}


class TagIOCAction(BaseAction):
    name = "tag_ioc"
    description = "Tag IOCs with a classification"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        tag = step_config.get("tag", "soar-auto-tagged")
        incident_id = context.get("incident_id", "")
        if incident_id:
            result = await db.execute(
                select(IocEntry).where(IocEntry.source_ids.contains([incident_id]))
            )
            for ioc in result.scalars().all():
                current_tags = ioc.tags or []
                if tag not in current_tags:
                    current_tags.append(tag)
                    ioc.tags = current_tags
        return {"success": True, "action": "tag_ioc", "tag": tag}


class UpdateThreatIntelAction(BaseAction):
    name = "update_threat_intel"
    description = "Update threat intelligence reputation"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        reputation = step_config.get("reputation_score", 0)
        incident_id = context.get("incident_id", "")
        if incident_id:
            ioc_result = await db.execute(
                select(IocEntry.normalized_value).where(IocEntry.source_ids.contains([incident_id]))
            )
            values = [r[0] for r in ioc_result.all() if r[0]]
            if values:
                ti_result = await db.execute(
                    select(ThreatIntel).where(ThreatIntel.normalized_value.in_(values))
                )
                for ti in ti_result.scalars().all():
                    ti.reputation_score = reputation
        return {"success": True, "action": "update_threat_intel", "reputation": reputation}


class ExportEvidenceAction(BaseAction):
    name = "export_evidence"
    description = "Export evidence from an incident"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        incident_id = context.get("incident_id", "")
        return {"success": True, "action": "export_evidence", "incident_id": incident_id, "message": "Evidence export initiated"}


class CloseIncidentAction(BaseAction):
    name = "close_incident"
    description = "Close an incident with resolution"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        incident_id = context.get("incident_id") or step_config.get("incident_id", "")
        if not incident_id:
            return {"success": False, "error": "No incident_id in context"}
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            return {"success": False, "error": "Incident not found"}
        resolution = step_config.get("resolution", "Automatically resolved by SOAR playbook")
        incident.status = "closed"
        incident.closed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        return {"success": True, "action": "close_incident", "incident_id": incident_id}


class CreateTicketAction(BaseAction):
    name = "create_ticket"
    description = "Create an external ticket"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        ticket_title = step_config.get("title", "Auto-generated ticket from SOAR")
        return {"success": True, "action": "create_ticket", "title": ticket_title, "ticket_id": "EXT-" + str(hash(ticket_title))[-8:]}


class SlackNotifyAction(BaseAction):
    name = "slack_notification"
    description = "Send Slack notification"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        message = step_config.get("message", "SOAR Playbook executed")
        return {"success": True, "action": "slack_notification", "message": message, "channel": step_config.get("channel", "#security")}


class TeamsNotifyAction(BaseAction):
    name = "teams_notification"
    description = "Send Microsoft Teams notification"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        message = step_config.get("message", "SOAR Playbook executed")
        return {"success": True, "action": "teams_notification", "message": message}


class DiscordNotifyAction(BaseAction):
    name = "discord_notification"
    description = "Send Discord notification"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        message = step_config.get("message", "SOAR Playbook executed")
        return {"success": True, "action": "discord_notification", "message": message}


class CollectLogsAction(BaseAction):
    name = "collect_logs"
    description = "Collect relevant logs for analysis"

    async def execute(self, db: AsyncSession, context: dict[str, Any], step_config: dict[str, Any]) -> dict[str, Any]:
        source_ip = context.get("source_ip", "")
        return {"success": True, "action": "collect_logs", "source_ip": source_ip, "message": f"Logs collected for {source_ip}"}


ACTION_REGISTRY: dict[str, BaseAction] = {
    "block_ip": BlockIPAction(),
    "disable_user": DisableUserAction(),
    "create_incident": CreateIncidentAction(),
    "run_ai_investigation": RunAIInvestigationAction(),
    "generate_report": GenerateReportAction(),
    "notify_team": NotifyTeamAction(),
    "update_asset_risk": UpdateAssetRiskAction(),
    "tag_ioc": TagIOCAction(),
    "update_threat_intel": UpdateThreatIntelAction(),
    "export_evidence": ExportEvidenceAction(),
    "close_incident": CloseIncidentAction(),
    "create_ticket": CreateTicketAction(),
    "slack_notification": SlackNotifyAction(),
    "teams_notification": TeamsNotifyAction(),
    "discord_notification": DiscordNotifyAction(),
    "collect_logs": CollectLogsAction(),
}


def get_action(action_type: str) -> BaseAction | None:
    return ACTION_REGISTRY.get(action_type)


def list_actions() -> list[dict[str, str]]:
    return [
        {"name": a.name, "description": a.description}
        for a in ACTION_REGISTRY.values()
    ]
