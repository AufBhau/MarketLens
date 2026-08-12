from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select

from marketlens.db import SessionLocal, get_engine, init_db
from marketlens.models import CaseStudy
from marketlens.schemas import MarketIntelligenceReport
from marketlens.services.report import build_report_from_case


CASES_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def load_cases_from_yaml() -> list[dict]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            cases.append(yaml.safe_load(f))
    return cases


def load_cases(*, prefer_db: bool = True) -> list[dict]:
    """Load demo cases from Postgres when available; fall back to YAML."""
    if prefer_db:
        try:
            init_db()
            engine = get_engine()
            SessionLocal.configure(bind=engine)
            session = SessionLocal()
            try:
                rows = session.scalars(select(CaseStudy).order_by(CaseStudy.slug)).all()
                if rows:
                    return [r.payload for r in rows]
            finally:
                session.close()
        except Exception:
            pass
    return load_cases_from_yaml()


def case_options(cases: list[dict]) -> dict[str, dict]:
    return {
        f"{c['company']} → {c['target_market']} ({c['industry']})": c for c in cases
    }


def generate_report(
    case: dict,
    scenario_overrides: dict | None = None,
) -> MarketIntelligenceReport:
    return build_report_from_case(case, scenario_overrides=scenario_overrides)
