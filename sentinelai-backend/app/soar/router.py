from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.soar import AutomationAction, Playbook, PlaybookExecution, PlaybookExecutionLog
from app.models.user import User
from app.notifications.service import create_notification
from app.schemas.base import APIResponse, PaginatedResponse
from app.schemas.soar import (
    ApprovalAction,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ExecuteResponse,
    PlaybookCreate,
    PlaybookExecutionLogResponse,
    PlaybookExecutionResponse,
    PlaybookListItem,
    PlaybookResponse,
    PlaybookStats,
    PlaybookUpdate,
)
from app.soar import playbook_service as pbs
from app.soar.action_registry import list_actions
from app.soar.approval import approve_request, create_approval_request, list_pending_approvals
from app.soar.executor import execute_playbook
from app.soar.scheduler import schedule_playbook

router = APIRouter()


@router.get("/actions", response_model=APIResponse[list])
async def get_actions(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return APIResponse(data=list_actions())


@router.get("/templates", response_model=APIResponse[list])
async def get_templates(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return APIResponse(data=pbs.get_template_list())


@router.post("/templates/{template_type}/instantiate", response_model=APIResponse[PlaybookResponse])
async def instantiate_template(
    template_type: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    name: str | None = Query(None),
):
    pb = await pbs.create_from_template(db, template_type, name=name, created_by=current_user.full_name)
    if not pb:
        raise HTTPException(status_code=404, detail=f"Template '{template_type}' not found")
    return APIResponse(data=pb.to_dict(), message="Playbook created from template")


@router.get("/stats", response_model=APIResponse[PlaybookStats])
async def get_playbook_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stats = await pbs.get_playbook_stats(db)
    return APIResponse(data=PlaybookStats(**stats))


@router.get("", response_model=APIResponse[PaginatedResponse[PlaybookListItem]])
async def list_playbooks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    playbook_type: str | None = Query(None),
    severity: str | None = Query(None),
):
    items, total = await pbs.list_playbooks(db, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order, search=search, playbook_type=playbook_type, severity=severity)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[PlaybookListItem(**i.to_dict()) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1,
    ))


@router.post("", response_model=APIResponse[PlaybookResponse], status_code=201)
async def create_playbook(
    body: PlaybookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    pb = await pbs.create_playbook(db, body, created_by=current_user.full_name)
    return APIResponse(data=PlaybookResponse(**pb.to_dict()), message="Playbook created")


@router.get("/{playbook_id}", response_model=APIResponse[PlaybookResponse])
async def get_playbook(
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    pb = await pbs.get_playbook(db, playbook_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return APIResponse(data=PlaybookResponse(**pb.to_dict()))


@router.put("/{playbook_id}", response_model=APIResponse[PlaybookResponse])
async def update_playbook(
    playbook_id: str,
    body: PlaybookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    pb = await pbs.update_playbook(db, playbook_id, body)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return APIResponse(data=PlaybookResponse(**pb.to_dict()), message="Playbook updated")


@router.delete("/{playbook_id}", response_model=APIResponse[dict])
async def delete_playbook(
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deleted = await pbs.delete_playbook(db, playbook_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return APIResponse(data={}, message="Playbook deleted")


@router.post("/{playbook_id}/execute", response_model=APIResponse[ExecuteResponse])
async def execute_playbook_endpoint(
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    incident_id: str | None = Query(None),
):
    try:
        execution = await execute_playbook(
            db, playbook_id=playbook_id,
            incident_id=incident_id,
            triggered_by=current_user.full_name,
        )
        return APIResponse(data=ExecuteResponse(
            execution_id=execution.id,
            status=execution.status,
            message=f"Playbook execution {execution.status}",
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/executions", response_model=APIResponse[PaginatedResponse[PlaybookExecutionResponse]])
async def list_executions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    playbook_id: str | None = Query(None),
):
    query = select(PlaybookExecution).order_by(PlaybookExecution.created_at.desc())
    if status:
        query = query.where(PlaybookExecution.status == status)
    if playbook_id:
        query = query.where(PlaybookExecution.playbook_id == playbook_id)
    total_query = select(PlaybookExecution.id)
    if status:
        total_query = total_query.where(PlaybookExecution.status == status)
    if playbook_id:
        total_query = total_query.where(PlaybookExecution.playbook_id == playbook_id)
    total = (await db.execute(total_query)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    items = result.scalars().all()
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[PlaybookExecutionResponse(**i.to_dict()) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1,
    ))


@router.get("/executions/{execution_id}", response_model=APIResponse[PlaybookExecutionResponse])
async def get_execution(
    execution_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(PlaybookExecution).where(PlaybookExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return APIResponse(data=PlaybookExecutionResponse(**execution.to_dict()))


@router.get("/executions/{execution_id}/logs", response_model=APIResponse[list])
async def get_execution_logs(
    execution_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(PlaybookExecutionLog)
        .where(PlaybookExecutionLog.execution_id == execution_id)
        .order_by(PlaybookExecutionLog.created_at)
    )
    logs = result.scalars().all()
    return APIResponse(data=[PlaybookExecutionLogResponse(**l.to_dict()) for l in logs])


@router.post("/{playbook_id}/retry", response_model=APIResponse[ExecuteResponse])
async def retry_playbook(
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    incident_id: str | None = Query(None),
):
    return await execute_playbook_endpoint(playbook_id, db, current_user, incident_id)


@router.get("/approvals/pending", response_model=APIResponse[PaginatedResponse[ApprovalRequestResponse]])
async def list_pending_approvals_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await list_pending_approvals(db, page=page, page_size=page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[ApprovalRequestResponse(**i.to_dict()) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1,
    ))


@router.post("/approvals/{request_id}/resolve", response_model=APIResponse[ApprovalRequestResponse])
async def resolve_approval(
    request_id: str,
    body: ApprovalAction,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    req = await approve_request(
        db, request_id, approved=body.approve,
        approved_by=current_user.full_name, reason=body.reason,
    )
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if body.approve:
        exec_result = await db.execute(
            select(PlaybookExecution).where(PlaybookExecution.id == req.execution_id)
        )
        execution = exec_result.scalar_one_or_none()
        if execution and execution.status == "awaiting_approval":
            from app.soar.executor import _run_steps
            from app.soar.playbook_service import get_playbook
            pb = await get_playbook(db, req.playbook_id)
            if pb and pb.steps:
                exec_context = execution.execution_data or {}
                exec_context["execution_id"] = execution.id
                if execution.incident_id:
                    exec_context["incident_id"] = execution.incident_id
                execution.status = "running"
                try:
                    await _run_steps(db, pb, execution, pb.steps, exec_context)
                    # Re-fetch execution to get updated status
                    await db.refresh(execution)
                except Exception as e:
                    execution.status = "failed"
                    execution.error_message = str(e)

    return APIResponse(data=ApprovalRequestResponse(**req.to_dict()), message="Approval resolved")


@router.post("/schedule", response_model=APIResponse[ExecuteResponse])
async def schedule_playbook_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    playbook_id: str = Query(...),
    trigger_event: str = Query("manual"),
    incident_id: str | None = Query(None),
):
    execution = await schedule_playbook(
        db, playbook_id=playbook_id, trigger_event=trigger_event,
        incident_id=incident_id,
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Playbook not found or inactive")
    return APIResponse(data=ExecuteResponse(
        execution_id=execution.id,
        status=execution.status,
        message=f"Playbook scheduled as {execution.status}",
    ))
