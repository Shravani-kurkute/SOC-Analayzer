from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.incident_response.comments import add_comment, get_comments
from app.incident_response.evidence import get_evidence_list
from app.incident_response.tasks import get_task_counts, get_tasks, update_task as update_task_db
from app.incident_response.timeline import add_timeline_entry, get_timeline
from app.models.incident import Incident
from app.models.incident_evidence import IncidentEvidence
from app.models.incident_task import IncidentTask
from app.models.user import User


class IncidentResponseService:

    async def create_incident(
        self,
        db: AsyncSession,
        title: str,
        severity: str,
        created_by: str,
        description: str | None = None,
        category: str | None = None,
        alert_ids: list[str] | None = None,
        asset_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            status="new",
            category=category,
            alert_ids=alert_ids or [],
            asset_ids=asset_ids or [],
            created_by=created_by,
        )
        db.add(incident)
        await db.flush()
        await db.refresh(incident)

        await add_timeline_entry(
            db, incident.id, "created", created_by,
            f"Incident created with severity {severity}",
        )

        return await self._to_detail(incident, db)

    async def get_incident(self, db: AsyncSession, incident_id: str) -> dict[str, Any] | None:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            return None
        return await self._to_detail(incident, db)

    async def update_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        actor: str,
        **kwargs,
    ) -> dict[str, Any] | None:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            return None

        status_change = kwargs.get("status") and kwargs["status"] != incident.status
        severity_change = kwargs.get("severity") and kwargs["severity"] != incident.severity

        for key, val in kwargs.items():
            if val is not None and hasattr(incident, key) and key != "alert_ids":
                if key == "alert_ids":
                    setattr(incident, key, val)
                else:
                    setattr(incident, key, val)

        if status_change:
            await add_timeline_entry(
                db, incident.id, "status_changed", actor,
                f"Status changed to {kwargs['status']}",
            )
            if kwargs["status"] in ("closed", "false_positive"):
                incident.closed_at = datetime.now(timezone.utc)
            else:
                incident.closed_at = None

        if severity_change:
            await add_timeline_entry(
                db, incident.id, "severity_changed", actor,
                f"Severity changed to {kwargs['severity']}",
            )

        await db.flush()
        await db.refresh(incident)
        return await self._to_detail(incident, db)

    async def list_incidents(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        severity: str | None = None,
        status: str | None = None,
        assignee_id: str | None = None,
        search: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        query = select(Incident)
        count_query = select(func.count(Incident.id))

        if severity:
            query = query.where(Incident.severity == severity)
            count_query = count_query.where(Incident.severity == severity)
        if status:
            query = query.where(Incident.status == status)
            count_query = count_query.where(Incident.status == status)
        if assignee_id:
            query = query.where(Incident.assignee_id == assignee_id)
            count_query = count_query.where(Incident.assignee_id == assignee_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(Incident.title.ilike(pattern) | (Incident.description.ilike(pattern)))
            count_query = count_query.where(Incident.title.ilike(pattern) | (Incident.description.ilike(pattern)))

        sort_col = getattr(Incident, sort_by, Incident.created_at)
        order = sort_col.asc() if sort_order == "asc" else sort_col.desc()
        query = query.order_by(order).offset((page - 1) * page_size).limit(page_size)

        total = await db.scalar(count_query)
        result = await db.execute(query)
        items = result.scalars().all()

        return [await self._to_list_item(i, db) for i in items], total or 0

    async def assign_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        user_id: str,
        actor: str,
    ) -> dict[str, Any] | None:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            return None

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        old_assignee = incident.assignee_id
        incident.assignee_id = user_id
        if incident.status == "new":
            incident.status = "assigned"

        await add_timeline_entry(
            db, incident.id, "assigned", actor,
            f"Assigned to {user.full_name}",
            {"previous_assignee": old_assignee},
        )

        await db.flush()
        return await self._to_detail(incident, db)

    async def close_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        actor: str,
        resolution: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any] | None:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            return None

        incident.status = "closed"
        incident.closed_at = datetime.now(timezone.utc)

        await add_timeline_entry(
            db, incident.id, "closed", actor,
            f"Incident closed. Resolution: {resolution or 'N/A'}",
            {"resolution": resolution, "notes": notes},
        )

        await db.flush()
        return await self._to_detail(incident, db)

    async def add_comment(
        self,
        db: AsyncSession,
        incident_id: str,
        user_id: str,
        user_name: str,
        content: str,
    ) -> dict[str, Any]:
        comment = await add_comment(db, incident_id, user_id, user_name, content)
        await add_timeline_entry(
            db, incident_id, "comment_added", user_name,
            "Added a comment",
        )
        return self._comment_to_dict(comment)

    async def edit_comment(
        self, db: AsyncSession, comment_id: str, user_id: str, content: str
    ) -> dict[str, Any] | None:
        from app.incident_response.comments import edit_comment as edit_comment_db
        comment = await edit_comment_db(db, comment_id, user_id, content)
        return self._comment_to_dict(comment) if comment else None

    async def delete_comment(self, db: AsyncSession, comment_id: str, user_id: str) -> bool:
        from app.incident_response.comments import delete_comment as delete_comment_db
        return await delete_comment_db(db, comment_id, user_id)

    async def create_task(
        self,
        db: AsyncSession,
        incident_id: str,
        title: str,
        actor: str,
        description: str | None = None,
        priority: str = "medium",
        assignee_id: str | None = None,
        due_date: datetime | None = None,
    ) -> dict[str, Any]:
        assignee_name = None
        if assignee_id:
            user_result = await db.execute(select(User).where(User.id == assignee_id))
            user = user_result.scalar_one_or_none()
            if user:
                assignee_name = user.full_name

        from app.incident_response.tasks import create_task as create_task_db
        task = await create_task_db(
            db, incident_id, title, description, priority,
            assignee_id, assignee_name, due_date,
        )
        await add_timeline_entry(
            db, incident_id, "task_created", actor,
            f"Task created: {title}",
        )
        return self._task_to_dict(task)

    async def update_task(
        self, db: AsyncSession, task_id: str, actor: str, **kwargs
    ) -> dict[str, Any] | None:
        task_result = await db.execute(select(IncidentTask).where(IncidentTask.id == task_id))
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        old_status = task.status
        updated = await update_task_db(db, task_id, **kwargs)
        if not updated:
            return None

        if kwargs.get("status") and kwargs["status"] != old_status:
            await add_timeline_entry(
                db, task.incident_id, "task_updated", actor,
                f"Task '{task.title}' status changed to {kwargs['status']}",
            )

        return self._task_to_dict(updated)

    async def upload_evidence(
        self,
        db: AsyncSession,
        incident_id: str,
        filename: str,
        file_data: bytes,
        uploaded_by: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        from app.incident_response.evidence import upload_evidence as upload_evidence_db
        evidence = await upload_evidence_db(
            db, incident_id, filename, file_data, uploaded_by, description,
        )
        await add_timeline_entry(
            db, incident_id, "evidence_uploaded", uploaded_by,
            f"Evidence uploaded: {filename}",
        )
        return self._evidence_to_dict(evidence)

    async def get_stats(self, db: AsyncSession) -> dict[str, Any]:
        total = await db.scalar(select(func.count(Incident.id))) or 0

        by_status = {}
        for row in (await db.execute(
            select(Incident.status, func.count(Incident.id))
            .group_by(Incident.status)
        )).all():
            by_status[row[0]] = row[1]

        by_severity = {}
        for row in (await db.execute(
            select(Incident.severity, func.count(Incident.id))
            .group_by(Incident.severity)
        )).all():
            by_severity[row[0]] = row[1]

        open_count = await db.scalar(
            select(func.count(Incident.id)).where(
                Incident.status.in_(["new", "assigned", "investigating", "contained", "eradiated", "recovered"])
            )
        ) or 0

        critical_count = await db.scalar(
            select(func.count(Incident.id)).where(Incident.severity == "critical")
        ) or 0

        closed_count = await db.scalar(
            select(func.count(Incident.id)).where(Incident.status == "closed")
        ) or 0

        avg_resolution = None
        if closed_count > 0:
            result = await db.execute(
                select(func.avg(
                    func.extract("epoch", Incident.closed_at - Incident.created_at)
                )).where(
                    Incident.closed_at.isnot(None),
                    Incident.created_at.isnot(None),
                )
            )
            avg_seconds = result.scalar()
            if avg_seconds:
                avg_resolution = int(avg_seconds)

        assignee_result = await db.execute(
            select(Incident.assignee_id, func.count(Incident.id))
            .where(Incident.assignee_id.isnot(None))
            .group_by(Incident.assignee_id)
            .order_by(func.count(Incident.id).desc())
            .limit(10)
        )
        by_analyst = {str(r[0]): r[1] for r in assignee_result}

        return {
            "total_incidents": total,
            "open_incidents": open_count,
            "critical_incidents": critical_count,
            "closed_incidents": closed_count,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_analyst": by_analyst,
            "avg_resolution_seconds": avg_resolution,
        }

    async def _to_detail(self, incident: Incident, db: AsyncSession) -> dict[str, Any]:
        comments = await get_comments(db, incident.id)
        tasks = await get_tasks(db, incident.id)
        evidence = await get_evidence_list(db, incident.id)
        timeline = await get_timeline(db, incident.id)

        assignee_name = None
        if incident.assignee_id:
            user_result = await db.execute(select(User).where(User.id == incident.assignee_id))
            user = user_result.scalar_one_or_none()
            if user:
                assignee_name = user.full_name

        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "category": incident.category,
            "alert_ids": incident.alert_ids or [],
            "asset_ids": incident.asset_ids or [],
            "assignee_id": incident.assignee_id,
            "assignee_name": assignee_name,
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
            "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
            "created_by": incident.created_by,
            "comments": [self._comment_to_dict(c) for c in comments],
            "tasks": [self._task_to_dict(t) for t in tasks],
            "evidence": [self._evidence_to_dict(e) for e in evidence],
            "timeline": [self._timeline_to_dict(t) for t in timeline],
        }

    async def _to_list_item(self, incident: Incident, db: AsyncSession) -> dict[str, Any]:
        task_total, task_done = await get_task_counts(db, incident.id)
        evidence_count = await db.scalar(
            select(func.count(IncidentEvidence.id))
            .where(IncidentEvidence.incident_id == incident.id)
        ) or 0

        assignee_name = None
        if incident.assignee_id:
            user_result = await db.execute(select(User).where(User.id == incident.assignee_id))
            user = user_result.scalar_one_or_none()
            if user:
                assignee_name = user.full_name

        return {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "category": incident.category,
            "assignee_id": incident.assignee_id,
            "assignee_name": assignee_name,
            "alert_count": len(incident.alert_ids) if incident.alert_ids else 0,
            "task_count": task_total,
            "task_done": task_done,
            "evidence_count": evidence_count,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
            "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
        }

    def _comment_to_dict(self, c: Any) -> dict[str, Any]:
        return {
            "id": c.id,
            "incident_id": c.incident_id,
            "author_id": c.author_id,
            "author_name": c.author_name,
            "content": c.content,
            "is_edited": c.is_edited,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }

    def _task_to_dict(self, t: Any) -> dict[str, Any]:
        return {
            "id": t.id,
            "incident_id": t.incident_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assignee_id": t.assignee_id,
            "assignee_name": t.assignee_name,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }

    def _evidence_to_dict(self, e: Any) -> dict[str, Any]:
        return {
            "id": e.id,
            "incident_id": e.incident_id,
            "filename": e.filename,
            "file_type": e.file_type,
            "file_size": e.file_size,
            "sha256": e.sha256,
            "uploaded_by": e.uploaded_by,
            "description": e.description,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }

    def _timeline_to_dict(self, t: Any) -> dict[str, Any]:
        return {
            "id": t.id,
            "incident_id": t.incident_id,
            "action": t.action,
            "actor": t.actor,
            "details": t.details,
            "metadata_json": t.metadata_json,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
