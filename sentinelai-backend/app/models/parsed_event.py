from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class ParsedEvent(BaseModel):
    __tablename__ = "parsed_events"

    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
