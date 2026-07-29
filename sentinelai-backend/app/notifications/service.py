from datetime import datetime, timezone

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationPreference
from app.notifications.websocket_manager import manager

logger = structlog.get_logger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: str,
    event_type: str,
    title: str,
    message: str | None = None,
    severity: str = "info",
    source: str | None = None,
    source_id: str | None = None,
    metadata_json: dict | None = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        event_type=event_type,
        title=title,
        message=message,
        severity=severity,
        source=source,
        source_id=source_id,
        metadata_json=metadata_json,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    await manager.send_to_user(user_id, {
        "type": "notification",
        "event": event_type,
        "notification": {
            "id": notif.id,
            "event_type": notif.event_type,
            "title": notif.title,
            "message": notif.message,
            "severity": notif.severity,
            "source": notif.source,
            "source_id": notif.source_id,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        },
    })

    return notif


async def notify_all_analysts(
    db: AsyncSession,
    event_type: str,
    title: str,
    message: str | None = None,
    severity: str = "info",
    source: str | None = None,
    source_id: str | None = None,
    metadata_json: dict | None = None,
    exclude_user_id: str | None = None,
) -> list[Notification]:
    from app.models.user import User
    users = (await db.execute(select(User.id))).scalars().all()
    created = []
    for uid in users:
        if exclude_user_id and uid == exclude_user_id:
            continue
        notif = await create_notification(
            db, uid, event_type, title, message,
            severity, source, source_id, metadata_json,
        )
        created.append(notif)
    return created


async def broadcast_event(
    event_type: str,
    data: dict,
) -> None:
    await manager.broadcast({
        "type": "event",
        "event": event_type,
        "data": data,
    })


async def get_user_notifications(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    event_type: str | None = None,
    severity: str | None = None,
) -> tuple[list[Notification], int]:
    query = select(Notification).where(Notification.user_id == user_id)
    count_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.is_read == False)
        count_query = count_query.where(Notification.is_read == False)
    if event_type:
        query = query.where(Notification.event_type == event_type)
        count_query = count_query.where(Notification.event_type == event_type)
    if severity:
        query = query.where(Notification.severity == severity)
        count_query = count_query.where(Notification.severity == severity)

    total = await db.scalar(count_query) or 0
    result = (await db.execute(
        query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    )).scalars().all()
    return list(result), total


async def get_unread_count(db: AsyncSession, user_id: str) -> int:
    return await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    ) or 0


async def mark_as_read(db: AsyncSession, notification_id: str, user_id: str) -> bool:
    notif = (await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )).scalar_one_or_none()
    if not notif:
        return False
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def mark_all_as_read(db: AsyncSession, user_id: str) -> int:
    from sqlalchemy import update
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount


async def delete_notification(db: AsyncSession, notification_id: str, user_id: str) -> bool:
    notif = (await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )).scalar_one_or_none()
    if not notif:
        return False
    await db.delete(notif)
    await db.commit()
    return True


async def clear_all_notifications(db: AsyncSession, user_id: str) -> int:
    from sqlalchemy import delete as sa_delete
    result = await db.execute(
        sa_delete(Notification).where(Notification.user_id == user_id)
    )
    await db.commit()
    return result.rowcount


async def get_preferences(db: AsyncSession, user_id: str) -> NotificationPreference:
    pref = (await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )).scalar_one_or_none()
    if not pref:
        pref = NotificationPreference(user_id=user_id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


async def update_preferences(
    db: AsyncSession,
    user_id: str,
    updates: dict,
) -> NotificationPreference:
    pref = await get_preferences(db, user_id)
    for key, value in updates.items():
        if hasattr(pref, key):
            setattr(pref, key, value)
    await db.commit()
    await db.refresh(pref)
    return pref
