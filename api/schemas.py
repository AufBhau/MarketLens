from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from marketlens.schemas import EngagementBrief, MarketIntelligenceReport, Objective


class CaseSummary(BaseModel):
    slug: str
    company: str
    industry: str
    target_market: str
    objective: str
    key_question: str | None = None
    label: str


class GenerateFromCaseRequest(BaseModel):
    slug: str
    scenario_overrides: dict[str, Any] | None = None


class CustomBriefRequest(BaseModel):
    company: str = Field(min_length=1)
    industry: str = Field(min_length=1)
    target_market: str = Field(min_length=1)
    objective: Objective = Objective.MARKET_ENTRY
    key_question: str | None = None
    scenario_overrides: dict[str, Any] | None = None


class ScenarioRecomputeRequest(BaseModel):
    slug: str | None = None
    brief: EngagementBrief | None = None
    expected_share_pct: float = Field(ge=0.1, le=20)
    entry_investment: float = Field(gt=0)
    annual_growth_pct: float = Field(ge=0, le=50)
    price_index: float = Field(gt=0, le=3)
    # When recomputing custom briefs, client may send the case slug of the pack used
    pack_slug: str | None = None


class GenerateResponse(BaseModel):
    report: MarketIntelligenceReport
    pack_slug: str
    note: str | None = None


class PdfExportRequest(BaseModel):
    report: MarketIntelligenceReport


class NarrativePolishRequest(BaseModel):
    report: MarketIntelligenceReport


class NarrativePolishResponse(BaseModel):
    report: MarketIntelligenceReport
    note: str = (
        "AI polished memo wording only. Scores and ENTER/HOLD/EXIT were not changed."
    )
