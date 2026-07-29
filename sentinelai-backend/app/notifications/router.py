from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.notifications import service as notify_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("")
async def list_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    event_type: str | None = Query(None),
    severity: str | None = Query(None),
):
    notifications, total = await notify_service.get_user_notifications(
        db, current_user.id, limit=limit, offset=offset,
        unread_only=unread_only, event_type=event_type, severity=severity,
    )
    return {
        "items": [
            {
                "id": n.id,
                "event_type": n.event_type,
                "title": n.title,
                "message": n.message,
                "severity": n.severity,
                "source": n.source,
                "source_id": n.source_id,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ],
        "total": total,
    }


@router.get("/unread-count")
async def unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    count = await notify_service.get_unread_count(db, current_user.id)
    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    success = await notify_service.mark_as_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(404, "Notification not found")
    return {"detail": "Marked as read"}


@router.post("/read-all")
async def mark_all_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    count = await notify_service.mark_all_as_read(db, current_user.id)
    return {"detail": f"{count} notifications marked as read", "count": count}


@router.delete("/{notification_id}")
async def delete_one(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    success = await notify_service.delete_notification(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(404, "Notification not found")
    return {"detail": "Notification deleted"}


@router.delete("")
async def clear_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    count = await notify_service.clear_all_notifications(db, current_user.id)
    return {"detail": f"{count} notifications cleared", "count": count}


@router.get("/preferences")
async def get_preferences(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    pref = await notify_service.get_preferences(db, current_user.id)
    return {
        "email_enabled": pref.email_enabled,
        "desktop_enabled": pref.desktop_enabled,
        "slack_enabled": pref.slack_enabled,
        "discord_enabled": pref.discord_enabled,
        "teams_enabled": pref.teams_enabled,
        "telegram_enabled": pref.telegram_enabled,
        "critical_only": pref.critical_only,
        "muted_until": pref.muted_until.isoformat() if pref.muted_until else None,
        "event_subscriptions": pref.event_subscriptions or {},
    }


@router.put("/preferences")
async def update_preferences(
    body: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    pref = await notify_service.update_preferences(db, current_user.id, body)
    return {"detail": "Preferences updated"}
