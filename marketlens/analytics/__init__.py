"""Analytics package — deterministic scoring models (LLM must not own these)."""

from marketlens.analytics.competition import analyze_competition
from marketlens.analytics.customers import analyze_customers
from marketlens.analytics.geography import analyze_geography, compute_mas
from marketlens.analytics.market import score_market_attractiveness
from marketlens.analytics.recommendation import recommend
from marketlens.analytics.scenarios import run_scenarios

__all__ = [
    "analyze_competition",
    "analyze_customers",
    "analyze_geography",
    "compute_mas",
    "recommend",
    "run_scenarios",
    "score_market_attractiveness",
]
