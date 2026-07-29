import structlog

from app.notifications.templates import render_email_template
from app.core.config import settings

logger = structlog.get_logger(__name__)


async def send_email(
    to: str,
    subject: str,
    template_name: str,
    context: dict | None = None,
) -> bool:
    try:
        html = render_email_template(template_name, context or {})
        logger.info("email_sent", to=to, subject=subject, template=template_name)
        return True
    except Exception as e:
        logger.error("email_failed", to=to, subject=subject, error=str(e))
        return False


async def send_critical_incident_email(user_email: str, incident_title: str, incident_id: str, severity: str) -> None:
    await send_email(
        to=user_email,
        subject=f"[CRITICAL] New {severity.upper()} Incident: {incident_title}",
        template_name="critical_incident",
        context={"title": incident_title, "incident_id": incident_id, "severity": severity},
    )


async def send_critical_ioc_email(user_email: str, ioc_value: str, ioc_type: str) -> None:
    await send_email(
        to=user_email,
        subject=f"[CRITICAL] IOC Detected: {ioc_value}",
        template_name="critical_ioc",
        context={"ioc_value": ioc_value, "ioc_type": ioc_type},
    )


async def send_threat_match_email(user_email: str, ioc_value: str, threat_type: str) -> None:
    await send_email(
        to=user_email,
        subject=f"[THREAT] Threat Intelligence Match: {ioc_value}",
        template_name="threat_match",
        context={"ioc_value": ioc_value, "threat_type": threat_type},
    )


async def send_ai_complete_email(user_email: str, incident_title: str) -> None:
    await send_email(
        to=user_email,
        subject=f"AI Investigation Complete: {incident_title}",
        template_name="ai_complete",
        context={"incident_title": incident_title},
    )


async def send_daily_report_email(user_email: str, summary: dict) -> None:
    await send_email(
        to=user_email,
        subject="SentinelAI Daily SOC Report",
        template_name="daily_report",
        context=summary,
    )


async def send_weekly_report_email(user_email: str, summary: dict) -> None:
    await send_email(
        to=user_email,
        subject="SentinelAI Weekly SOC Report",
        template_name="weekly_report",
        context=summary,
    )
