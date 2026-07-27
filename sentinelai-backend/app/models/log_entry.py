from datetime import datetime
from typing import Any
from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class LogEntry(BaseModel):
    __tablename__ = "log_entries"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    action: Mapped[str | None] = mapped_column(String(20), nullable=True)
    log_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bytes_sent: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    bytes_received: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    threat_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
