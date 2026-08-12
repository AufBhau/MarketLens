from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from marketlens.db import Base

# JSON works on both Postgres and SQLite (Postgres still preferred in production).
JSONType = JSON


class CaseStudy(Base):
    __tablename__ = "case_studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    company: Mapped[str] = mapped_column(String(128))
    industry: Mapped[str] = mapped_column(String(128))
    target_market: Mapped[str] = mapped_column(String(128))
    objective: Mapped[str] = mapped_column(String(64))
    key_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONType)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Engagement(Base):
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(128))
    industry: Mapped[str] = mapped_column(String(128))
    target_market: Mapped[str] = mapped_column(String(128))
    objective: Mapped[str] = mapped_column(String(64))
    key_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    entry_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
