from datetime import datetime, timezone

import structlog
from sqlalchemy import func, select

from app.models.incident import Incident
from app.models.user import User
from app.notifications.email import send_daily_report_email, send_weekly_report_email

logger = structlog.get_logger(__name__)


async def get_daily_summary(db_session_factory) -> dict:
    async with db_session_factory() as db:
        total = await db.scalar(select(func.count(Incident.id))) or 0
        critical = await db.scalar(
            select(func.count(Incident.id)).where(Incident.severity == "critical")
        ) or 0
        resolved = await db.scalar(
            select(func.count(Incident.id)).where(Incident.status.in_(["closed", "resolved"]))
        ) or 0
        return {"total_incidents": total, "critical": critical, "resolved": resolved}


async def send_daily_reports(db_session_factory) -> None:
    summary = await get_daily_summary(db_session_factory)
    async with db_session_factory() as db:
        users = (await db.execute(select(User.email).where(User.is_active == True))).scalars().all()
    for email in users:
        if email:
            await send_daily_report_email(email, summary)
    logger.info("daily_reports_sent", user_count=len(users))


async def send_weekly_reports(db_session_factory) -> None:
    summary = await get_daily_summary(db_session_factory)
    async with db_session_factory() as db:
        users = (await db.execute(select(User.email).where(User.is_active == True))).scalars().all()
    for email in users:
        if email:
            await send_weekly_report_email(email, summary)
    logger.info("weekly_reports_sent", user_count=len(users))
