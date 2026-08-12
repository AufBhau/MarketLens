from __future__ import annotations

import json

from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from marketlens.config import get_settings
from marketlens.schemas import MarketIntelligenceReport


class PolishedNarrative(BaseModel):
    narrative: str = Field(description="Executive summary narrative, 2-4 sentences")
    why: list[str] = Field(description="Exactly 4 concise reasons supporting the recommendation")
    recommended_strategy: str = Field(description="One short strategy paragraph")
    priority_actions: list[str] = Field(
        description="Exactly 4 priority actions, short and actionable"
    )


SYSTEM_PROMPT = """You are a consulting associate writing client-ready memo language for MarketLens.
You receive a structured market intelligence report produced by deterministic models.
Your job is ONLY to polish the written narrative.

Hard rules:
- Do NOT change the recommendation action (ENTER/HOLD/EXIT/EXPAND).
- Do NOT invent new market sizes, competitors, geographies, or numbers.
- Do NOT contradict the provided scores or findings.
- Keep claims grounded in the supplied JSON only.
- Tone: clear, senior, concise, consulting-style. No hype. No emojis.
- Respond with ONLY valid JSON matching this schema:
{
  "narrative": "string",
  "why": ["string", "string", "string", "string"],
  "recommended_strategy": "string",
  "priority_actions": ["string", "string", "string", "string"]
}
"""


def _compact_context(report: MarketIntelligenceReport) -> dict:
    return {
        "brief": report.brief.model_dump(),
        "recommendation_action": report.recommendation.action.value,
        "entry_score": report.recommendation.overall_confidence,
        "executive_labels": {
            "market_attractiveness": report.executive_summary.market_attractiveness,
            "competitive_intensity": report.executive_summary.competitive_intensity,
            "customer_opportunity": report.executive_summary.customer_opportunity,
            "entry_risk": report.executive_summary.entry_risk,
        },
        "market_overall": report.market.overall,
        "market_dimensions": [d.model_dump() for d in report.market.dimensions],
        "whitespace": report.competition.whitespace_insight,
        "positioning": report.competition.recommended_positioning,
        "intensity": report.competition.intensity_score,
        "target_segment": report.customers.recommended_segment,
        "segment_rationale": report.customers.rationale,
        "top_markets": report.geography.top_markets,
        "scenarios": {
            "base_score": report.scenarios.base.score,
            "base_roi_pct": report.scenarios.base.roi_pct,
            "base_risk": report.scenarios.base.risk_score,
            "conservative_score": report.scenarios.conservative.score,
            "aggressive_score": report.scenarios.aggressive.score,
        },
        "current_narrative": report.executive_summary.narrative,
        "current_why": report.recommendation.why,
        "current_strategy": report.recommendation.recommended_strategy,
        "current_actions": report.recommendation.priority_actions,
    }


def polish_narrative(report: MarketIntelligenceReport) -> PolishedNarrative:
    settings = get_settings()
    if not settings.mistral_api_key:
        raise HTTPException(
            status_code=400,
            detail="MISTRAL_API_KEY is not set. Add it to .env to enable AI narrative polish.",
        )

    # Mistral exposes an OpenAI-compatible API
    client = OpenAI(
        api_key=settings.mistral_api_key,
        base_url=settings.mistral_base_url,
    )
    context = _compact_context(report)

    try:
        completion = client.chat.completions.create(
            model=settings.mistral_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Polish this MarketLens report memo. Keep all facts unchanged.\n\n"
                        + json.dumps(context, ensure_ascii=True)
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except Exception as exc:  # noqa: BLE001 - surface provider errors cleanly
        raise HTTPException(
            status_code=502,
            detail=f"Mistral API request failed: {exc}",
        ) from exc

    content = completion.choices[0].message.content
    if not content:
        raise HTTPException(status_code=502, detail="Mistral returned an empty response.")

    try:
        polished = PolishedNarrative.model_validate_json(content)
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Mistral returned invalid JSON for narrative polish: {exc}",
        ) from exc

    if len(polished.why) < 4:
        polished.why = (polished.why + report.recommendation.why)[:4]
    else:
        polished.why = polished.why[:4]

    if len(polished.priority_actions) < 4:
        polished.priority_actions = (
            polished.priority_actions + report.recommendation.priority_actions
        )[:4]
    else:
        polished.priority_actions = polished.priority_actions[:4]

    return polished


def apply_polish(
    report: MarketIntelligenceReport, polished: PolishedNarrative
) -> MarketIntelligenceReport:
    updated = report.model_copy(deep=True)
    updated.executive_summary.narrative = polished.narrative
    updated.executive_summary.priority_actions = list(polished.priority_actions)
    updated.recommendation.why = list(polished.why)
    updated.recommendation.recommended_strategy = polished.recommended_strategy
    updated.recommendation.priority_actions = list(polished.priority_actions)
    return updated


def maybe_polish_report(
    report: MarketIntelligenceReport,
) -> tuple[MarketIntelligenceReport, bool, str | None]:
    """
    Auto-polish when Mistral is configured.
    Returns (report, polished?, warning).
    Never blocks report generation on LLM failure.
    """
    settings = get_settings()
    if not settings.mistral_api_key:
        return report, False, None
    try:
        polished = polish_narrative(report)
        return apply_polish(report, polished), True, None
    except HTTPException as exc:
        return report, False, str(exc.detail)
    except Exception as exc:  # noqa: BLE001
        return report, False, f"AI narrative polish skipped: {exc}"
