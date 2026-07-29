from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class AIInvestigation(BaseModel):
    __tablename__ = "ai_investigations"

    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    attack_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline_data: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    mitre_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ioc_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    containment: Mapped[str | None] = mapped_column(Text, nullable=True)
    recovery: Mapped[str | None] = mapped_column(Text, nullable=True)
    hunting_queries: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    false_positive_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
