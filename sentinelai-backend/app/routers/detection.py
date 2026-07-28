from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.detection.engine import DetectionEngine
from app.detection.registry import DetectionRuleRegistry
from app.models.parsed_event import ParsedEvent
from app.models.user import User
from app.schemas.detection import (
    DetectionRunRequest,
    DetectionRunResponse,
    DetectionStatusResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter()
engine = DetectionEngine()


@router.post("/run", response_model=DetectionRunResponse)
async def run_detection(
    request: DetectionRunRequest,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    stmt = select(ParsedEvent).order_by(ParsedEvent.created_at.desc()).limit(1000)
    if request.event_ids:
        stmt = select(ParsedEvent).where(ParsedEvent.id.in_(request.event_ids))
    result = await db.execute(stmt)
    parsed_events = result.scalars().all()

    if not parsed_events:
        raise HTTPException(status_code=400, detail="No parsed events found to analyze")

    events_data = [
        pe.to_dict() if hasattr(pe, "to_dict") else {"id": str(pe.id), "raw": pe.raw_data}
        for pe in parsed_events
    ]

    if request.rule_ids:
        alerts = []
        for rule_id in request.rule_ids:
            detection_result = await engine.run_rule(rule_id, events_data, db)
            if detection_result:
                alert = engine._create_alert_from_result(detection_result, db)
                alerts.append(alert)
        if alerts:
            await db.commit()
    else:
        alerts = await engine.run_all_for_parsed(events_data, db)

    return DetectionRunResponse(
        alerts_created=len(alerts),
        alerts=[{"id": str(a.id), "title": a.title, "severity": a.severity, "score": a.score} for a in alerts],
    )


@router.post("/run-all", response_model=DetectionRunResponse)
async def run_all_detection(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    stmt = select(ParsedEvent).order_by(ParsedEvent.created_at.desc()).limit(1000)
    result = await db.execute(stmt)
    parsed_events = result.scalars().all()

    if not parsed_events:
        raise HTTPException(status_code=400, detail="No parsed events found to analyze")

    events_data = [
        pe.to_dict() if hasattr(pe, "to_dict") else {"id": str(pe.id), "raw": pe.raw_data}
        for pe in parsed_events
    ]

    alerts = await engine.run_all_for_parsed(events_data, db)

    return DetectionRunResponse(
        alerts_created=len(alerts),
        alerts=[{"id": str(a.id), "title": a.title, "severity": a.severity, "score": a.score} for a in alerts],
    )


@router.get("/rules", response_model=list[dict])
async def list_detection_rules(
    category: str | None = Query(None),
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    rules = DetectionRuleRegistry.get_rules_by_category(category) if category else DetectionRuleRegistry.get_all()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "description": r.get("description"),
            "category": r.get("category"),
            "severity": r.get("severity"),
            "risk_score": r.get("risk_score"),
            "mitre_mapping": r.get("mitre_mapping"),
            "enabled": r.get("enabled", True),
        }
        for r in rules
    ]


@router.get("/status", response_model=DetectionStatusResponse)
async def get_detection_status(
    _current_user: Annotated[User, Depends(get_current_user)] = None,
):
    return DetectionStatusResponse(
        total_rules=len(DetectionRuleRegistry.get_all()),
        enabled_rules=len(DetectionRuleRegistry.get_enabled()),
        modules_loaded=list(engine.modules.keys()),
    )
