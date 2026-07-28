from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.correlation_event import CorrelationEvent as CorrelationEventModel
from app.models.correlation_group import CorrelationGroup as CorrelationGroupModel
from app.models.user import User
from app.schemas.correlation import (
    CorrelationGroupListSchema,
    CorrelationGroupSchema,
    CorrelationRunResult,
    CorrelationStats,
)
from app.services.correlation.engine import CorrelationEngine

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/run", response_model=CorrelationRunResult)
async def run_correlation(
    rule_name: str | None = Query(None, description="Run a specific rule by name"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    engine = CorrelationEngine(db)
    if rule_name:
        from app.services.correlation.rules import CorrelationRuleRegistry
        rule = CorrelationRuleRegistry.get(rule_name)
        if not rule:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"Correlation rule '{rule_name}' not found")
        result = await engine.run_rule(rule)
    else:
        result = await engine.run_all_rules()

    await db.commit()
    logger.info("Correlation run complete", **result)
    return CorrelationRunResult(**result)


@router.post("/run-all", response_model=CorrelationRunResult)
async def run_all_correlations(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    engine = CorrelationEngine(db)
    result = await engine.run_all_rules()
    await db.commit()
    logger.info("Full correlation run complete", **result)
    return CorrelationRunResult(**result)


@router.get("", response_model=list[CorrelationGroupListSchema])
async def list_correlation_groups(
    group_type: str | None = Query(None),
    status: str | None = Query(None),
    source_ip: str | None = Query(None),
    username: str | None = Query(None),
    min_risk: float | None = Query(None, ge=0, le=10),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    stmt = select(CorrelationGroupModel).order_by(CorrelationGroupModel.start_time.desc())

    if group_type:
        stmt = stmt.where(CorrelationGroupModel.group_type == group_type)
    if status:
        stmt = stmt.where(CorrelationGroupModel.status == status)
    if source_ip:
        stmt = stmt.where(CorrelationGroupModel.source_ip == source_ip)
    if username:
        stmt = stmt.where(CorrelationGroupModel.username == username)
    if min_risk is not None:
        stmt = stmt.where(CorrelationGroupModel.risk_score >= min_risk)

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    groups = result.scalars().all()
    return [CorrelationGroupListSchema.model_validate(g) for g in groups]


@router.get("/stats", response_model=CorrelationStats)
async def get_correlation_stats(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    total = await db.scalar(select(func.count(CorrelationGroupModel.id)))
    open_count = await db.scalar(
        select(func.count(CorrelationGroupModel.id)).where(CorrelationGroupModel.status == "open")
    )
    avg_risk = await db.scalar(select(func.avg(CorrelationGroupModel.risk_score))) or 0.0
    total_events = await db.scalar(select(func.count(CorrelationEventModel.id))) or 0

    type_rows = await db.execute(
        select(CorrelationGroupModel.group_type, func.count(CorrelationGroupModel.id))
        .group_by(CorrelationGroupModel.group_type)
    )
    groups_by_type = dict(type_rows.all())

    status_rows = await db.execute(
        select(CorrelationGroupModel.status, func.count(CorrelationGroupModel.id))
        .group_by(CorrelationGroupModel.status)
    )
    groups_by_status = dict(status_rows.all())

    return CorrelationStats(
        total_groups=total or 0,
        open_groups=open_count or 0,
        avg_risk_score=round(float(avg_risk), 2),
        total_events_correlated=total_events,
        groups_by_type=groups_by_type,
        groups_by_status=groups_by_status,
    )


@router.get("/{group_id}", response_model=CorrelationGroupSchema)
async def get_correlation_group(
    group_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    from app.core.exceptions import NotFoundError

    stmt = select(CorrelationGroupModel).where(CorrelationGroupModel.id == group_id)
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        raise NotFoundError("Correlation group")

    events_stmt = select(CorrelationEventModel).where(CorrelationEventModel.group_id == group_id)
    events_result = await db.execute(events_stmt)
    events = events_result.scalars().all()

    group_dict = CorrelationGroupSchema.model_validate(group)
    group_dict.events = [
        {
            "id": str(e.id),
            "group_id": str(e.group_id),
            "parsed_event_id": e.parsed_event_id,
            "log_entry_id": e.log_entry_id,
            "event_type": e.event_type,
            "event_source": e.event_source,
            "source_ip": e.source_ip,
            "destination_ip": e.destination_ip,
            "username": e.username,
            "timestamp": e.timestamp,
            "action": e.action,
            "severity": e.severity,
            "risk_score": e.risk_score,
            "raw_message": e.raw_message,
            "metadata": e.metadata,
            "created_at": e.created_at,
        }
        for e in events
    ]
    return group_dict
