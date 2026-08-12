from __future__ import annotations

from marketlens.schemas import MarketAttractiveness, ScoreDimension


def score_market_attractiveness(
    *,
    market_size_score: float,
    growth_score: float,
    competition_score: float,
    demand_score: float,
    weights: dict[str, float] | None = None,
    underpenetrated: list[str] | None = None,
    rationales: dict[str, str] | None = None,
) -> MarketAttractiveness:
    """Weighted market attractiveness. High competitive intensity lowers attractiveness."""
    weights = weights or {
        "market_size": 0.25,
        "growth": 0.30,
        "competition": 0.20,
        "demand": 0.25,
    }
    rationales = rationales or {}
    competition_attractiveness = 100 - competition_score

    dims = [
        ScoreDimension(
            name="Market Size",
            score=market_size_score,
            rationale=rationales.get("market_size", ""),
        ),
        ScoreDimension(
            name="Growth",
            score=growth_score,
            rationale=rationales.get("growth", ""),
        ),
        ScoreDimension(
            name="Competition",
            score=competition_attractiveness,
            rationale=rationales.get("competition", ""),
        ),
        ScoreDimension(
            name="Demand",
            score=demand_score,
            rationale=rationales.get("demand", ""),
        ),
    ]

    overall = (
        weights["market_size"] * market_size_score
        + weights["growth"] * growth_score
        + weights["competition"] * competition_attractiveness
        + weights["demand"] * demand_score
    )
    return MarketAttractiveness(
        dimensions=dims,
        overall=round(overall, 1),
        high_growth_underpenetrated=underpenetrated or [],
    )
