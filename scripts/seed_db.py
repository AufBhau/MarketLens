from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from sqlalchemy import select

from marketlens.db import SessionLocal, get_engine, init_db
from marketlens.models import CaseStudy


CASES_DIR = ROOT / "data" / "cases"


def load_case_files() -> list[dict]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            cases.append(yaml.safe_load(f))
    return cases


def seed(replace: bool = False) -> None:
    init_db()
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        for case in load_case_files():
            existing = session.scalar(
                select(CaseStudy).where(CaseStudy.slug == case["slug"])
            )
            if existing and not replace:
                print(f"skip {case['slug']} (exists)")
                continue
            if existing and replace:
                session.delete(existing)
                session.flush()
            row = CaseStudy(
                slug=case["slug"],
                company=case["company"],
                industry=case["industry"],
                target_market=case["target_market"],
                objective=case["objective"],
                key_question=case.get("key_question"),
                payload=case,
            )
            session.add(row)
            print(f"seeded {case['slug']}")
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed MarketLens demo cases")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing case studies with the same slug",
    )
    args = parser.parse_args()
    seed(replace=args.replace)
