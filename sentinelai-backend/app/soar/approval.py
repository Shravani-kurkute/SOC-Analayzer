from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.soar import ApprovalRequest


async def create_approval_request(
    db: AsyncSession,
    playbook_id: str,
    execution_id: str,
    incident_id: str | None,
    step_index: int,
    action_type: str,
    requested_by: str | None = None,
    reason: str | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> ApprovalRequest:
    req = ApprovalRequest(
        playbook_id=playbook_id,
        execution_id=execution_id,
        incident_id=incident_id,
        step_index=step_index,
        action_type=action_type,
        requested_by=requested_by,
        status="pending",
        reason=reason,
        metadata_json=metadata_json,
    )
    db.add(req)
    await db.flush()
    await db.refresh(req)
    return req


async def approve_request(
    db: AsyncSession,
    request_id: str,
    approved: bool,
    approved_by: str | None = None,
    reason: str | None = None,
) -> ApprovalRequest | None:
    result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        return None
    req.status = "approved" if approved else "rejected"
    req.approved_by = approved_by
    req.reason = reason
    req.resolved_at = datetime.now(timezone.utc)
    return req


async def list_pending_approvals(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ApprovalRequest], int]:
    query = select(ApprovalRequest).where(ApprovalRequest.status == "pending").order_by(ApprovalRequest.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return list(result.scalars().all()), total


async def get_pending_count(db: AsyncSession) -> int:
    return await db.scalar(
        select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == "pending")
    ) or 0
