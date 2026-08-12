from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response

from api import services
from api.schemas import (
    CaseSummary,
    CustomBriefRequest,
    GenerateFromCaseRequest,
    GenerateResponse,
    NarrativePolishRequest,
    NarrativePolishResponse,
    PdfExportRequest,
    ScenarioRecomputeRequest,
)
from marketlens.services.narrative import apply_polish, polish_narrative
from marketlens.services.pdf_export import build_report_pdf

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/cases", response_model=list[CaseSummary])
def list_cases() -> list[CaseSummary]:
    return services.list_case_summaries()


@router.get("/cases/{slug}")
def get_case(slug: str) -> dict:
    return services.get_case_payload(slug)


@router.post("/reports/from-case", response_model=GenerateResponse)
def report_from_case(body: GenerateFromCaseRequest) -> GenerateResponse:
    return services.generate_from_case(body)


@router.post("/reports/from-brief", response_model=GenerateResponse)
def report_from_brief(body: CustomBriefRequest) -> GenerateResponse:
    return services.generate_from_custom(body)


@router.post("/reports/scenarios", response_model=GenerateResponse)
def report_scenarios(body: ScenarioRecomputeRequest) -> GenerateResponse:
    return services.recompute_scenarios(body)


@router.post("/reports/export-pdf")
def export_pdf(body: PdfExportRequest) -> Response:
    pdf_bytes = build_report_pdf(body.report)
    company = body.report.brief.company.lower().replace(" ", "-")
    filename = f"marketlens-{company}-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/reports/polish-narrative", response_model=NarrativePolishResponse)
def polish_report_narrative(body: NarrativePolishRequest) -> NarrativePolishResponse:
    polished = polish_narrative(body.report)
    report = apply_polish(body.report, polished)
    return NarrativePolishResponse(report=report)
