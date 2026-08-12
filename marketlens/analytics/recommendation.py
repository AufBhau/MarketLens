from __future__ import annotations

from marketlens.schemas import (
    CustomerAnalysis,
    CompetitiveIntelligence,
    ExecutiveSummary,
    GeographicAnalysis,
    MarketAttractiveness,
    RecommendationAction,
    ScenarioAnalysis,
    StrategicRecommendation,
)


def _label(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 55:
        return "Moderate"
    return "Low"


def recommend(
    *,
    market: MarketAttractiveness,
    competition: CompetitiveIntelligence,
    customers: CustomerAnalysis,
    geography: GeographicAnalysis,
    scenarios: ScenarioAnalysis,
    objective: str,
) -> tuple[StrategicRecommendation, ExecutiveSummary]:
    base = scenarios.base
    entry_score = round(
        0.30 * market.overall
        + 0.20 * (100 - competition.intensity_score)
        + 0.15
        * next(
            (
                s.attractiveness
                for s in customers.segments
                if s.name == customers.recommended_segment
            ),
            60,
        )
        + 0.15 * (geography.opportunities[0].mas if geography.opportunities else 50)
        + 0.20 * base.score,
        1,
    )

    if entry_score >= 70:
        action = (
            RecommendationAction.EXPAND
            if "Expansion" in objective
            else RecommendationAction.ENTER
        )
    elif entry_score >= 55:
        action = RecommendationAction.HOLD
    else:
        action = RecommendationAction.EXIT

    why = [
        f"Attractive market — overall attractiveness {market.overall:.0f}/100 "
        f"with growth dimension "
        f"{next(d.score for d in market.dimensions if d.name == 'Growth'):.0f}/100.",
        f"Competitive opportunity — {competition.whitespace_insight}",
        f"Customer opportunity — recommend targeting {customers.recommended_segment}: "
        f"{customers.rationale}",
        f"Financial attractiveness — base-case score {base.score:.0f}/100 "
        f"(ROI {base.roi_pct:.0f}%, break-even {base.break_even_years} yrs).",
    ]

    strategy = (
        f"Prioritize {customers.recommended_segment}; enter via "
        f"{competition.recommended_positioning}; focus geography on "
        f"{', '.join(geography.top_markets[:3]) or 'highest-MAS regions'}; "
        f"differentiate rather than compete purely on price."
    )

    priorities = [
        f"Target segment: {customers.recommended_segment}",
        f"Prioritize markets: {', '.join(geography.top_markets[:3])}",
        f"Adopt positioning: {competition.recommended_positioning}",
        "Validate assumptions through primary customer research",
    ]

    rec = StrategicRecommendation(
        action=action,
        why=why,
        recommended_strategy=strategy,
        priority_actions=priorities,
        overall_confidence=entry_score,
    )

    narrative = (
        f"The market demonstrates {_label(market.overall).lower()} attractiveness "
        f"and {_label(100 - competition.intensity_score).lower()} competitive headroom. "
        f"Customer opportunity is concentrated in {customers.recommended_segment}. "
        f"Base-case economics support a **{action.value}** posture, with priority focus on "
        f"{', '.join(geography.top_markets[:3])}."
    ).replace("**", "")

    summary = ExecutiveSummary(
        market_attractiveness=_label(market.overall),
        competitive_intensity=_label(competition.intensity_score),
        customer_opportunity=_label(
            next(
                (
                    s.attractiveness
                    for s in customers.segments
                    if s.name == customers.recommended_segment
                ),
                60,
            )
        ),
        entry_risk=_label(base.risk_score),
        overall_recommendation=action,
        narrative=narrative,
        priority_actions=priorities,
    )
    return rec, summary
