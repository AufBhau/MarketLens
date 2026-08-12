from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from marketlens.schemas import MarketIntelligenceReport


NAVY = colors.HexColor("#0b1f33")
BLUE = colors.HexColor("#2563eb")
MUTED = colors.HexColor("#6b7280")
LINE = colors.HexColor("#e5e7eb")
SOFT = colors.HexColor("#f3f5f8")


def build_report_pdf(report: MarketIntelligenceReport) -> bytes:
    """Build a consulting-style one/two-page PDF from a MarketIntelligenceReport."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"MarketLens — {report.brief.company}",
        author="MarketLens",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Brand",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=BLUE,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=NAVY,
            spaceAfter=4,
            leading=22,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=MUTED,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MlBullet",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            leftIndent=10,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RecAction",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=colors.white,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RecMeta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.white,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Foot",
            parent=styles["Normal"],
            fontSize=7.5,
            textColor=MUTED,
            leading=10,
            spaceBefore=12,
        )
    )

    story: list = []
    brief = report.brief
    ex = report.executive_summary
    rec = report.recommendation

    story.append(Paragraph("MARKETLENS · MARKET INTELLIGENCE", styles["Brand"]))
    story.append(
        Paragraph(
            f"{brief.company} — Strategic Market Intelligence Report",
            styles["DocTitle"],
        )
    )
    story.append(
        Paragraph(
            f"{brief.industry} · {brief.target_market} · {brief.objective.value}",
            styles["Meta"],
        )
    )
    if brief.key_question:
        story.append(
            Paragraph(f"<b>Client question:</b> {brief.key_question}", styles["Body"])
        )

    # Recommendation banner
    banner = Table(
        [
            [
                Paragraph(f"RECOMMENDATION: {rec.action.value}", styles["RecAction"]),
                Paragraph(
                    f"Entry score<br/><b>{rec.overall_confidence:.0f}/100</b>",
                    styles["RecMeta"],
                ),
            ]
        ],
        colWidths=[125 * mm, 40 * mm],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(banner)
    story.append(Spacer(1, 8))
    story.append(Paragraph(ex.narrative, styles["Body"]))

    # KPI table
    story.append(Paragraph("Executive snapshot", styles["Section"]))
    kpi_data = [
        ["Market", "Competition", "Customers", "Entry risk", "Decision"],
        [
            ex.market_attractiveness,
            ex.competitive_intensity,
            ex.customer_opportunity,
            ex.entry_risk,
            ex.overall_recommendation.value,
        ],
    ]
    kpi = Table(kpi_data, colWidths=[33 * mm] * 5)
    kpi.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SOFT),
                ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 11),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(kpi)

    # Market scores
    story.append(Paragraph("Market attractiveness", styles["Section"]))
    market_rows = [["Dimension", "Score", "Rationale"]]
    for d in report.market.dimensions:
        market_rows.append(
            [
                d.name,
                f"{d.score:.0f}",
                Paragraph(d.rationale or "—", styles["MlBullet"]),
            ]
        )
    market_rows.append(["Overall", f"{report.market.overall:.0f}", ""])
    market_tbl = Table(market_rows, colWidths=[32 * mm, 18 * mm, 115 * mm])
    market_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SOFT),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(market_tbl)

    # Competition / customers / geo highlights
    story.append(Paragraph("Key findings", styles["Section"]))
    story.append(
        Paragraph(
            f"<b>Competitive whitespace:</b> {report.competition.whitespace_insight}",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Positioning:</b> {report.competition.recommended_positioning}",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Target segment:</b> {report.customers.recommended_segment} — "
            f"{report.customers.rationale}",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Priority geographies:</b> {', '.join(report.geography.top_markets)}",
            styles["Body"],
        )
    )

    # Scenarios
    story.append(Paragraph("Scenario scores", styles["Section"]))
    s = report.scenarios
    scen_rows = [
        ["Scenario", "Score", "ROI %", "Break-even (yrs)", "Risk"],
        [
            "Conservative",
            f"{s.conservative.score:.0f}",
            f"{s.conservative.roi_pct:.0f}",
            f"{s.conservative.break_even_years if s.conservative.break_even_years is not None else '—'}",
            f"{s.conservative.risk_score:.0f}",
        ],
        [
            "Base case",
            f"{s.base.score:.0f}",
            f"{s.base.roi_pct:.0f}",
            f"{s.base.break_even_years if s.base.break_even_years is not None else '—'}",
            f"{s.base.risk_score:.0f}",
        ],
        [
            "Aggressive",
            f"{s.aggressive.score:.0f}",
            f"{s.aggressive.roi_pct:.0f}",
            f"{s.aggressive.break_even_years if s.aggressive.break_even_years is not None else '—'}",
            f"{s.aggressive.risk_score:.0f}",
        ],
    ]
    scen_tbl = Table(scen_rows, colWidths=[35 * mm, 25 * mm, 25 * mm, 40 * mm, 25 * mm])
    scen_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SOFT),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#eff4ff")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(scen_tbl)

    # Why + strategy
    story.append(Paragraph("Why this recommendation", styles["Section"]))
    for i, reason in enumerate(rec.why, 1):
        story.append(Paragraph(f"<b>{i}.</b> {reason}", styles["MlBullet"]))

    story.append(Paragraph("Recommended strategy", styles["Section"]))
    story.append(Paragraph(rec.recommended_strategy, styles["Body"]))

    story.append(Paragraph("Priority actions", styles["Section"]))
    for item in rec.priority_actions:
        story.append(Paragraph(f"• {item}", styles["MlBullet"]))

    assumptions = report.assumptions or {}
    vintage = assumptions.get("data_vintage", "Illustrative estimates")
    note = assumptions.get("note", "")
    story.append(
        Paragraph(
            f"<b>Assumptions:</b> {vintage}"
            + (f" · {note}" if note else "")
            + " · Generated by MarketLens. Figures are directional and should be "
            "validated with primary research before real decisions.",
            styles["Foot"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
