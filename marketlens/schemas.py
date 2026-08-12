from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Objective(str, Enum):
    MARKET_ENTRY = "Market Entry"
    MARKET_EXPANSION = "Market Expansion"
    COMPETITIVE_ANALYSIS = "Competitive Analysis"
    NEW_PRODUCT = "New Product Opportunity"
    PRICING = "Pricing Analysis"


class RecommendationAction(str, Enum):
    ENTER = "ENTER"
    HOLD = "HOLD"
    EXIT = "EXIT"
    EXPAND = "EXPAND"


class EngagementBrief(BaseModel):
    company: str
    industry: str
    target_market: str
    objective: Objective
    key_question: str | None = None


class ScoreDimension(BaseModel):
    name: str
    score: float = Field(ge=0, le=100)
    rationale: str = ""


class MarketAttractiveness(BaseModel):
    dimensions: list[ScoreDimension]
    overall: float = Field(ge=0, le=100)
    high_growth_underpenetrated: list[str] = Field(default_factory=list)


class CompetitorProfile(BaseModel):
    name: str
    revenue_bn: float | None = None
    market_share_pct: float | None = None
    pricing_position: str
    products: list[str] = Field(default_factory=list)
    geography: list[str] = Field(default_factory=list)
    customer_segment: str
    value_proposition: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    x_innovation: float = Field(ge=0, le=100, description="Positioning map X")
    y_premium: float = Field(ge=0, le=100, description="Positioning map Y")


class CompetitiveIntelligence(BaseModel):
    competitors: list[CompetitorProfile]
    intensity_score: float = Field(ge=0, le=100)
    whitespace_insight: str
    recommended_positioning: str


class CustomerSegment(BaseModel):
    name: str
    description: str
    income_level: str
    price_sensitivity: str
    brand_sensitivity: str
    share_of_demand_pct: float
    attractiveness: float = Field(ge=0, le=100)


class CustomerAnalysis(BaseModel):
    segments: list[CustomerSegment]
    recommended_segment: str
    rationale: str


class GeoOpportunity(BaseModel):
    region: str
    mas: float = Field(ge=0, le=100)
    drivers: dict[str, float] = Field(default_factory=dict)


class GeographicAnalysis(BaseModel):
    opportunities: list[GeoOpportunity]
    top_markets: list[str]
    methodology_note: str


class ScenarioResult(BaseModel):
    name: str
    expected_share_pct: float
    entry_investment: float
    annual_growth_pct: float
    price_index: float
    revenue_potential: float
    profit_potential: float
    break_even_years: float | None
    roi_pct: float
    risk_score: float
    score: float = Field(ge=0, le=100)


class ScenarioAnalysis(BaseModel):
    currency: str = "USD"
    conservative: ScenarioResult
    base: ScenarioResult
    aggressive: ScenarioResult


class StrategicRecommendation(BaseModel):
    action: RecommendationAction
    why: list[str]
    recommended_strategy: str
    priority_actions: list[str]
    overall_confidence: float = Field(ge=0, le=100)


class ExecutiveSummary(BaseModel):
    market_attractiveness: str
    competitive_intensity: str
    customer_opportunity: str
    entry_risk: str
    overall_recommendation: RecommendationAction
    narrative: str
    priority_actions: list[str]


class MarketIntelligenceReport(BaseModel):
    brief: EngagementBrief
    market: MarketAttractiveness
    competition: CompetitiveIntelligence
    customers: CustomerAnalysis
    geography: GeographicAnalysis
    scenarios: ScenarioAnalysis
    recommendation: StrategicRecommendation
    executive_summary: ExecutiveSummary
    assumptions: dict[str, Any] = Field(default_factory=dict)
    case_id: str | None = None
