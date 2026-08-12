from __future__ import annotations

from marketlens.schemas import GeographicAnalysis, GeoOpportunity


def compute_mas(
    drivers: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Market Attractiveness Score = Σ w_i * driver_i (drivers already 0–100)."""
    total_w = sum(weights.values()) or 1.0
    score = sum(weights.get(k, 0.0) * v for k, v in drivers.items()) / total_w
    # Include weighted dims even if missing from drivers as 0
    for k, w in weights.items():
        if k not in drivers:
            score += 0.0 * w / total_w
    return round(min(100.0, max(0.0, score)), 1)


def analyze_geography(
    opportunities: list[GeoOpportunity],
    *,
    top_n: int = 3,
    methodology_note: str = "",
) -> GeographicAnalysis:
    ranked = sorted(opportunities, key=lambda o: o.mas, reverse=True)
    return GeographicAnalysis(
        opportunities=ranked,
        top_markets=[o.region for o in ranked[:top_n]],
        methodology_note=methodology_note
        or "MAS uses industry-weighted growth, demand, purchasing power, competition (inverted), and accessibility.",
    )
