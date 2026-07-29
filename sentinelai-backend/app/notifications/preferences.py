from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationPreference


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
