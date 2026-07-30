from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.soar import Playbook, PlaybookExecution, PlaybookExecutionLog
from app.notifications.service import create_notification
from app.soar.action_registry import get_action
from app.soar.approval import create_approval_request
from app.soar.workflow import resolve_next_steps


async def execute_playbook(
    db: AsyncSession,
    playbook_id: str,
    incident_id: str | None = None,
    triggered_by: str | None = None,
    context: dict[str, Any] | None = None,
) -> PlaybookExecution:
    result = await db.execute(select(Playbook).where(Playbook.id == playbook_id))
    playbook = result.scalar_one_or_none()
    if not playbook:
        raise ValueError(f"Playbook {playbook_id} not found")

    steps = playbook.steps or []
    total_steps = len(steps)

    execution = PlaybookExecution(
        playbook_id=playbook_id,
        playbook_name=playbook.name,
        incident_id=incident_id,
        status="running",
        current_step=0,
        total_steps=total_steps,
        started_at=datetime.now(timezone.utc),
        triggered_by=triggered_by,
        execution_data=context or {},
    )
    db.add(execution)
    await db.flush()
    await db.refresh(execution)

    exec_context: dict[str, Any] = dict(context or {})
    exec_context["execution_id"] = execution.id
    if incident_id:
        exec_context["incident_id"] = incident_id

    try:
        await _run_steps(db, playbook, execution, steps, exec_context)
    except Exception as e:
        execution.status = "failed"
        execution.error_message = str(e)
        execution.completed_at = datetime.now(timezone.utc)
        if execution.started_at:
            execution.duration_ms = int((datetime.now(timezone.utc) - execution.started_at).total_seconds() * 1000)

    playbook.execution_count += 1
    if execution.status == "completed":
        old_total = playbook.execution_count - 1
        if old_total > 0:
            playbook.avg_execution_time = (
                (playbook.avg_execution_time * old_total) + (execution.duration_ms or 0)
            ) / playbook.execution_count
        else:
            playbook.avg_execution_time = float(execution.duration_ms or 0)
        old_rate = playbook.success_rate * old_total
        playbook.success_rate = (old_rate + 100) / playbook.execution_count
    else:
        old_rate = playbook.success_rate * (playbook.execution_count - 1)
        playbook.success_rate = old_rate / playbook.execution_count if playbook.execution_count > 0 else 0

    return execution


async def _run_steps(
    db: AsyncSession,
    playbook: Playbook,
    execution: PlaybookExecution,
    steps: list[dict[str, Any]],
    context: dict[str, Any],
) -> None:
    visited = set()
    current_indices = [0]

    while current_indices:
        idx = current_indices.pop(0)
        if idx in visited or idx >= len(steps):
            continue
        visited.add(idx)

        step = steps[idx]
        execution.current_step = idx
        step_name = step.get("name", f"Step {idx}")
        action_type = step.get("action", "")
        node_type = step.get("type", "action")
        step_config = step.get("config", {})

        start = time.monotonic()

        if node_type == "delay":
            delay_seconds = step_config.get("seconds", 5)
            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type="delay",
                status="completed",
                message=f"Delayed {delay_seconds}s",
                duration_ms=delay_seconds * 1000,
            )
            db.add(log_entry)
            next_indices = resolve_next_steps(steps, idx, context)
            current_indices = next_indices + current_indices
            continue

        if node_type == "approval":
            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type="approval",
                status="pending",
                message="Waiting for approval",
            )
            db.add(log_entry)
            await create_approval_request(
                db,
                playbook_id=playbook.id,
                execution_id=execution.id,
                incident_id=execution.incident_id,
                step_index=idx,
                action_type=action_type,
                requested_by=execution.triggered_by,
                reason=step_config.get("reason"),
            )
            execution.status = "awaiting_approval"
            next_indices = resolve_next_steps(steps, idx, context)
            current_indices = next_indices + current_indices
            continue

        if node_type == "condition":
            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type="condition",
                status="completed",
                message="Condition evaluated",
            )
            db.add(log_entry)
            next_indices = resolve_next_steps(steps, idx, context)
            current_indices = next_indices + current_indices
            continue

        action_obj = get_action(action_type)
        if not action_obj:
            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type=action_type,
                status="failed",
                message=f"Unknown action: {action_type}",
                error=f"No action registered for '{action_type}'",
            )
            db.add(log_entry)
            execution.failed_step = idx
            execution.status = "failed"
            execution.error_message = f"Unknown action at step {idx}: {action_type}"
            return

        try:
            result = await action_obj.execute(db, context, step_config)
            duration = int((time.monotonic() - start) * 1000)
            status = "completed" if result.get("success", False) else "failed"

            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type=action_type,
                status=status,
                message=result.get("message", result.get("action", "")),
                duration_ms=duration,
                input_data=step_config,
                output_data=result,
                error=result.get("error"),
            )
            db.add(log_entry)

            if not result.get("success", False):
                execution.failed_step = idx
                execution.status = "failed"
                execution.error_message = f"Step {idx} ({step_name}) failed: {result.get('error', 'Unknown error')}"
                return

            context.update(result)

        except Exception as e:
            duration = int((time.monotonic() - start) * 1000)
            log_entry = PlaybookExecutionLog(
                execution_id=execution.id,
                step_index=idx,
                step_name=step_name,
                action_type=action_type,
                status="failed",
                message=str(e),
                duration_ms=duration,
                error=str(e),
            )
            db.add(log_entry)
            execution.failed_step = idx
            execution.status = "failed"
            execution.error_message = f"Exception at step {idx} ({step_name}): {e}"
            return

        next_indices = resolve_next_steps(steps, idx, context)
        current_indices = next_indices + current_indices

    execution.status = "completed"
    execution.completed_at = datetime.now(timezone.utc)
    if execution.started_at:
        execution.duration_ms = int((datetime.now(timezone.utc) - execution.started_at).total_seconds() * 1000)
