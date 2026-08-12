from __future__ import annotations

from marketlens.schemas import ScenarioAnalysis, ScenarioResult


def _scenario(
    name: str,
    *,
    market_size: float,
    expected_share_pct: float,
    entry_investment: float,
    annual_growth_pct: float,
    price_index: float,
    margin_pct: float,
    horizon_years: int = 5,
) -> ScenarioResult:
    # Simplified consulting-style financial sketch (illustrative, not accounting-grade).
    year1_rev = market_size * (expected_share_pct / 100.0) * price_index
    growth = 1 + annual_growth_pct / 100.0
    revenues = [year1_rev * (growth**y) for y in range(horizon_years)]
    revenue_potential = sum(revenues)
    profit_potential = revenue_potential * (margin_pct / 100.0) - entry_investment
    annual_profit = (year1_rev * (margin_pct / 100.0)) if year1_rev else 0
    break_even = (
        round(entry_investment / annual_profit, 1) if annual_profit > 0 else None
    )
    roi_pct = (
        (profit_potential / entry_investment) * 100 if entry_investment else 0.0
    )
    # Risk rises with aggressiveness of share and investment intensity
    risk = min(
        100.0,
        20 + expected_share_pct * 8 + (entry_investment / max(market_size, 1)) * 40,
    )
    # Score blends ROI quality, break-even speed, and inverse risk (demo-calibrated).
    roi_component = min(100.0, max(0.0, 40 + roi_pct * 0.9))
    be_component = (
        100.0
        if break_even is None
        else max(0.0, 100.0 - (break_even * 8.0))
    )
    score = max(
        0.0,
        min(
            100.0,
            0.40 * roi_component + 0.35 * be_component + 0.25 * (100 - risk),
        ),
    )
    return ScenarioResult(
        name=name,
        expected_share_pct=expected_share_pct,
        entry_investment=entry_investment,
        annual_growth_pct=annual_growth_pct,
        price_index=price_index,
        revenue_potential=round(revenue_potential, 2),
        profit_potential=round(profit_potential, 2),
        break_even_years=break_even,
        roi_pct=round(roi_pct, 1),
        risk_score=round(risk, 1),
        score=round(score, 1),
    )


def run_scenarios(
    *,
    market_size: float,
    currency: str,
    margin_pct: float,
    conservative: dict,
    base: dict,
    aggressive: dict,
) -> ScenarioAnalysis:
    return ScenarioAnalysis(
        currency=currency,
        conservative=_scenario("Conservative", market_size=market_size, margin_pct=margin_pct, **conservative),
        base=_scenario("Base Case", market_size=market_size, margin_pct=margin_pct, **base),
        aggressive=_scenario("Aggressive", market_size=market_size, margin_pct=margin_pct, **aggressive),
    )
