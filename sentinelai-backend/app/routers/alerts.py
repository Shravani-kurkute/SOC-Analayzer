from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.alert import Alert as AlertModel
from app.models.user import User
from app.schemas.alert import AlertListResponse, AlertResponse, AlertStatsResponse, AlertUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    severity: str | None = Query(None),
    status: str | None = Query(None),
    rule_id: str | None = Query(None),
    source_ip: str | None = Query(None),
    mitre_tactic: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    stmt = select(AlertModel)

    if severity:
        stmt = stmt.where(AlertModel.severity == severity)
    if status:
        stmt = stmt.where(AlertModel.status == status)
    if rule_id:
        stmt = stmt.where(AlertModel.rule_id == rule_id)
    if source_ip:
        stmt = stmt.where(AlertModel.source_ip == source_ip)
    if mitre_tactic:
        stmt = stmt.where(AlertModel.mitre_tactic == mitre_tactic)
    if search:
        stmt = stmt.where(
            AlertModel.title.ilike(f"%{search}%")
            | AlertModel.description.ilike(f"%{search}%")
            | AlertModel.source_ip.ilike(f"%{search}%")
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    total_pages = max(1, (total + page_size - 1) // page_size)

    sort_col = getattr(AlertModel, sort_by, AlertModel.created_at)
    order_fn = sort_col.desc if sort_order == "desc" else sort_col.asc
    stmt = stmt.order_by(order_fn()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    alerts = result.scalars().all()

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    total = await db.scalar(select(func.count(AlertModel.id))) or 0

    severity_rows = await db.execute(
        select(AlertModel.severity, func.count(AlertModel.id))
        .group_by(AlertModel.severity)
    )
    by_severity = dict(severity_rows.all())

    status_rows = await db.execute(
        select(AlertModel.status, func.count(AlertModel.id))
        .group_by(AlertModel.status)
    )
    by_status = dict(status_rows.all())

    rule_rows = await db.execute(
        select(AlertModel.rule_name, func.count(AlertModel.id))
        .where(AlertModel.rule_name.isnot(None))
        .group_by(AlertModel.rule_name)
        .order_by(func.count(AlertModel.id).desc())
        .limit(10)
    )
    by_rule = dict(rule_rows.all())

    ip_rows = await db.execute(
        select(AlertModel.source_ip, func.count(AlertModel.id))
        .where(AlertModel.source_ip.isnot(None))
        .group_by(AlertModel.source_ip)
        .order_by(func.count(AlertModel.id).desc())
        .limit(10)
    )
    top_source_ips = [{"ip": ip, "count": cnt} for ip, cnt in ip_rows.all()]

    avg_score = await db.scalar(select(func.coalesce(func.avg(AlertModel.score), 0))) or 0.0

    trend_rows = await db.execute(
        select(
            func.date_trunc("day", AlertModel.created_at).label("day"),
            func.count(AlertModel.id),
        )
        .group_by(func.date_trunc("day", AlertModel.created_at))
        .order_by(func.date_trunc("day", AlertModel.created_at).desc())
        .limit(14)
    )
    recent_trend = [{"date": str(day), "count": cnt} for day, cnt in trend_rows.all()]

    return AlertStatsResponse(
        total=total,
        by_severity=by_severity,
        by_status=by_status,
        by_rule=by_rule,
        top_source_ips=top_source_ips,
        avg_score=round(float(avg_score), 2),
        recent_trend=recent_trend,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    from app.core.exceptions import NotFoundError

    stmt = select(AlertModel).where(AlertModel.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("Alert")
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    update: AlertUpdate,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    from app.core.exceptions import NotFoundError

    stmt = select(AlertModel).where(AlertModel.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("Alert")

    if update.status is not None:
        alert.status = update.status
        if update.status == "acknowledged":
            alert.acknowledged_by = current_user.email
            alert.acknowledged_at = func.now()
        elif update.status == "resolved":
            alert.resolved_by = current_user.email
            alert.resolved_at = func.now()
    if update.acknowledged_by is not None:
        alert.acknowledged_by = update.acknowledged_by
    if update.resolved_by is not None:
        alert.resolved_by = update.resolved_by
    if update.incident_id is not None:
        alert.incident_id = update.incident_id

    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    from app.core.exceptions import NotFoundError

    stmt = select(AlertModel).where(AlertModel.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("Alert")

    await db.delete(alert)
    await db.commit()
    return {"message": "Alert deleted successfully"}
