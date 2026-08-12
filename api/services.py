from __future__ import annotations

from fastapi import HTTPException

from marketlens.data_access import load_cases
from marketlens.schemas import Objective
from marketlens.services.narrative import maybe_polish_report
from marketlens.services.report import build_report_from_case

from api.schemas import (
    CaseSummary,
    CustomBriefRequest,
    GenerateFromCaseRequest,
    GenerateResponse,
    ScenarioRecomputeRequest,
)

INDUSTRY_PACK = {
    "Coffee & Retail": "starbucks-india-coffee",
    "Electric Vehicles": "tesla-germany-ev",
    "Healthcare": "pharma-india-healthcare",
    "Consumer Electronics": "starbucks-india-coffee",
    "Technology": "tesla-germany-ev",
}


def _cases_by_slug() -> dict[str, dict]:
    return {c["slug"]: c for c in load_cases()}


def list_case_summaries() -> list[CaseSummary]:
    out: list[CaseSummary] = []
    for c in load_cases():
        label = f"{c['company']} → {c['target_market']} ({c['industry']})"
        out.append(
            CaseSummary(
                slug=c["slug"],
                company=c["company"],
                industry=c["industry"],
                target_market=c["target_market"],
                objective=c["objective"],
                key_question=c.get("key_question"),
                label=label,
            )
        )
    return out


def get_case_payload(slug: str) -> dict:
    case = _cases_by_slug().get(slug)
    if not case:
        raise HTTPException(status_code=404, detail=f"Unknown case slug: {slug}")
    return case


def generate_from_case(body: GenerateFromCaseRequest) -> GenerateResponse:
    case = get_case_payload(body.slug)
    report = build_report_from_case(case, scenario_overrides=body.scenario_overrides)
    report, polished, polish_warning = maybe_polish_report(report)
    note = None
    if polished:
        note = "Memo wording auto-polished with Mistral. Scores and recommendation action unchanged."
    elif polish_warning:
        note = polish_warning
    return GenerateResponse(report=report, pack_slug=case["slug"], note=note)


def _nearest_pack_slug(industry: str) -> str:
    return INDUSTRY_PACK.get(industry, "starbucks-india-coffee")


def generate_from_custom(body: CustomBriefRequest) -> GenerateResponse:
    pack_slug = _nearest_pack_slug(body.industry)
    base = get_case_payload(pack_slug)
    case = {
        **base,
        "company": body.company,
        "industry": body.industry,
        "target_market": body.target_market,
        "objective": body.objective.value
        if isinstance(body.objective, Objective)
        else body.objective,
        "key_question": body.key_question,
        "slug": f"custom-{body.company.lower().replace(' ', '-')}",
    }
    report = build_report_from_case(case, scenario_overrides=body.scenario_overrides)
    report, polished, polish_warning = maybe_polish_report(report)

    notes = [
        "Custom briefs currently reuse the nearest industry research pack. "
        "Scores reflect that pack's structured data, not live diligence on the named company."
    ]
    if polished:
        notes.append(
            "Memo wording auto-polished with Mistral. Scores and recommendation action unchanged."
        )
    elif polish_warning:
        notes.append(polish_warning)

    return GenerateResponse(
        report=report,
        pack_slug=pack_slug,
        note=" ".join(notes),
    )


def recompute_scenarios(body: ScenarioRecomputeRequest) -> GenerateResponse:
    overrides = {
        "base": {
            "expected_share_pct": body.expected_share_pct,
            "entry_investment": body.entry_investment,
            "annual_growth_pct": body.annual_growth_pct,
            "price_index": body.price_index,
        }
    }

    if body.slug:
        return generate_from_case(
            GenerateFromCaseRequest(slug=body.slug, scenario_overrides=overrides)
        )

    if body.brief:
        return generate_from_custom(
            CustomBriefRequest(
                company=body.brief.company,
                industry=body.brief.industry,
                target_market=body.brief.target_market,
                objective=body.brief.objective,
                key_question=body.brief.key_question,
                scenario_overrides=overrides,
            )
        )

    raise HTTPException(
        status_code=400, detail="Provide either slug or brief to recompute scenarios."
    )
