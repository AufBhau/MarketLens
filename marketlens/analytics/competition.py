from __future__ import annotations

from marketlens.schemas import CompetitiveIntelligence, CompetitorProfile


def analyze_competition(
    competitors: list[CompetitorProfile],
    *,
    intensity_score: float,
    whitespace_insight: str,
    recommended_positioning: str,
) -> CompetitiveIntelligence:
    return CompetitiveIntelligence(
        competitors=competitors,
        intensity_score=intensity_score,
        whitespace_insight=whitespace_insight,
        recommended_positioning=recommended_positioning,
    )


def competitive_whitespace_heuristic(
    competitors: list[CompetitorProfile],
) -> str:
    """Simple rule: look for sparse mid-premium / mid-innovation quadrant."""
    if not competitors:
        return "Insufficient competitor coverage to identify whitespace."

    mid = [
        c
        for c in competitors
        if 35 <= c.x_innovation <= 65 and 35 <= c.y_premium <= 65
    ]
    if len(mid) <= max(1, len(competitors) // 4):
        return (
            "The mid-price / mid-innovation segment has relatively limited "
            "competition despite likely demand density — a potential whitespace."
        )
    crowded = max(competitors, key=lambda c: c.market_share_pct or 0)
    return (
        f"Competition clusters around established players such as {crowded.name}; "
        "differentiation on non-price attributes is required."
    )
