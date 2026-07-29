from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_task import IncidentTask


async def create_task(
    db: AsyncSession,
    incident_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    assignee_id: str | None = None,
    assignee_name: str | None = None,
    due_date: datetime | None = None,
) -> IncidentTask:
    task = IncidentTask(
        incident_id=incident_id,
        title=title,
        description=description,
        priority=priority,
        assignee_id=assignee_id,
        assignee_name=assignee_name,
        due_date=due_date,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task_id: str,
    **kwargs,
) -> IncidentTask | None:
    result = await db.execute(select(IncidentTask).where(IncidentTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None

    for key, val in kwargs.items():
        if val is not None and hasattr(task, key):
            setattr(task, key, val)

    if kwargs.get("status") == "completed" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)
    elif kwargs.get("status") and kwargs["status"] != "completed":
        task.completed_at = None

    await db.flush()
    await db.refresh(task)
    return task


async def get_tasks(db: AsyncSession, incident_id: str) -> list[IncidentTask]:
    result = await db.execute(
        select(IncidentTask)
        .where(IncidentTask.incident_id == incident_id)
        .order_by(IncidentTask.created_at.desc())
    )
    return list(result.scalars().all())


async def get_task_counts(db: AsyncSession, incident_id: str) -> tuple[int, int]:
    total = await db.scalar(
        select(func.count(IncidentTask.id)).where(IncidentTask.incident_id == incident_id)
    )
    done = await db.scalar(
        select(func.count(IncidentTask.id)).where(
            IncidentTask.incident_id == incident_id,
            IncidentTask.status == "completed",
        )
    )
    return total or 0, done or 0
