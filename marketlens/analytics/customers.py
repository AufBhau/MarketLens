from __future__ import annotations

from marketlens.schemas import CustomerAnalysis, CustomerSegment


def analyze_customers(segments: list[CustomerSegment]) -> CustomerAnalysis:
    if not segments:
        return CustomerAnalysis(
            segments=[],
            recommended_segment="N/A",
            rationale="No segment data available.",
        )
    best = max(segments, key=lambda s: s.attractiveness)
    return CustomerAnalysis(
        segments=segments,
        recommended_segment=best.name,
        rationale=(
            f"{best.name} offers the strongest blend of demand share "
            f"({best.share_of_demand_pct:.0f}%) and segment attractiveness "
            f"({best.attractiveness:.0f}/100)."
        ),
    )
