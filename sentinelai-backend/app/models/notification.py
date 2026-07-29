from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class NotificationPreference(BaseModel):
    __tablename__ = "notification_preferences"

    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    desktop_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    slack_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discord_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    teams_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    telegram_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    critical_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    muted_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_subscriptions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
