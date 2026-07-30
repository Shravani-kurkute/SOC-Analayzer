from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class Playbook(BaseModel):
    __tablename__ = "playbooks"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    playbook_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    steps: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class PlaybookExecution(BaseModel):
    __tablename__ = "playbook_executions"

    playbook_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    playbook_name: Mapped[str] = mapped_column(String(255), nullable=False)
    incident_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    failed_step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class PlaybookExecutionLog(BaseModel):
    __tablename__ = "playbook_execution_logs"

    execution_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class ApprovalRequest(BaseModel):
    __tablename__ = "approval_requests"

    playbook_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    execution_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    incident_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


class AutomationAction(BaseModel):
    __tablename__ = "automation_actions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
