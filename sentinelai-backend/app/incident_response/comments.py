from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_comment import IncidentComment


async def add_comment(
    db: AsyncSession,
    incident_id: str,
    author_id: str,
    author_name: str,
    content: str,
) -> IncidentComment:
    comment = IncidentComment(
        incident_id=incident_id,
        author_id=author_id,
        author_name=author_name,
        content=content,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def edit_comment(
    db: AsyncSession,
    comment_id: str,
    user_id: str,
    content: str,
) -> IncidentComment | None:
    result = await db.execute(
        select(IncidentComment).where(
            IncidentComment.id == comment_id,
            IncidentComment.author_id == user_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return None
    comment.content = content
    comment.is_edited = True
    await db.flush()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession,
    comment_id: str,
    user_id: str,
) -> bool:
    result = await db.execute(
        select(IncidentComment).where(
            IncidentComment.id == comment_id,
            IncidentComment.author_id == user_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return False
    await db.delete(comment)
    return True


async def get_comments(db: AsyncSession, incident_id: str) -> list[IncidentComment]:
    result = await db.execute(
        select(IncidentComment)
        .where(IncidentComment.incident_id == incident_id)
        .order_by(IncidentComment.created_at.asc())
    )
    return list(result.scalars().all())
