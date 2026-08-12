from __future__ import annotations

from typing import Any

from marketlens.analytics.competition import analyze_competition
from marketlens.analytics.customers import analyze_customers
from marketlens.analytics.geography import analyze_geography, compute_mas
from marketlens.analytics.market import score_market_attractiveness
from marketlens.analytics.recommendation import recommend
from marketlens.analytics.scenarios import run_scenarios
from marketlens.schemas import (
    CompetitorProfile,
    CustomerSegment,
    EngagementBrief,
    GeoOpportunity,
    MarketIntelligenceReport,
    Objective,
)


def build_report_from_case(
    case: dict[str, Any],
    *,
    scenario_overrides: dict[str, Any] | None = None,
) -> MarketIntelligenceReport:
    """Build a full report from a seeded case payload + optional slider overrides."""
    brief = EngagementBrief(
        company=case["company"],
        industry=case["industry"],
        target_market=case["target_market"],
        objective=Objective(case["objective"]),
        key_question=case.get("key_question"),
    )

    m = case["market"]
    market = score_market_attractiveness(
        market_size_score=m["market_size_score"],
        growth_score=m["growth_score"],
        competition_score=m["competition_intensity"],
        demand_score=m["demand_score"],
        weights=m.get("weights"),
        underpenetrated=m.get("underpenetrated"),
        rationales=m.get("rationales"),
    )

    competitors = [CompetitorProfile(**c) for c in case["competitors"]]
    competition = analyze_competition(
        competitors,
        intensity_score=case["competition_meta"]["intensity_score"],
        whitespace_insight=case["competition_meta"]["whitespace_insight"],
        recommended_positioning=case["competition_meta"]["recommended_positioning"],
    )

    segments = [CustomerSegment(**s) for s in case["segments"]]
    customers = analyze_customers(segments)

    geo_cfg = case["geography"]
    weights = geo_cfg["weights"]
    opportunities = []
    for row in geo_cfg["regions"]:
        drivers = row["drivers"]
        opportunities.append(
            GeoOpportunity(
                region=row["region"],
                mas=compute_mas(drivers, weights),
                drivers=drivers,
            )
        )
    geography = analyze_geography(
        opportunities,
        methodology_note=geo_cfg.get("methodology_note", ""),
    )

    fin = case["financials"]
    overrides = scenario_overrides or {}
    scenarios = run_scenarios(
        market_size=fin["market_size"],
        currency=fin.get("currency", "USD"),
        margin_pct=fin.get("margin_pct", 18),
        conservative={**fin["conservative"], **overrides.get("conservative", {})},
        base={**fin["base"], **overrides.get("base", {})},
        aggressive={**fin["aggressive"], **overrides.get("aggressive", {})},
    )

    recommendation, executive_summary = recommend(
        market=market,
        competition=competition,
        customers=customers,
        geography=geography,
        scenarios=scenarios,
        objective=brief.objective.value,
    )

    return MarketIntelligenceReport(
        brief=brief,
        market=market,
        competition=competition,
        customers=customers,
        geography=geography,
        scenarios=scenarios,
        recommendation=recommendation,
        executive_summary=executive_summary,
        assumptions=case.get("assumptions", {}),
        case_id=case.get("slug"),
    )
