"""SkillRadar MY — application entry point.

Run:  python src/main.py
Replit starts this file (see .replit). The Streamlit UI imports the same
helpers from ``src/utils.py`` so the demo and the tests share one engine.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import Role, pathway, rank, sdg_summary  # noqa: E402

# Synthetic demo profile — never a real CV (Domain 1 rule: public/synthetic data only).
DEMO_PROFILE = ["customer support", "excel", "team lead"]

ROLES = [
    Role(
        "AI Operations Specialist",
        ["prompt engineering", "data visualisation", "sql", "customer support"],
        trend=0.8,
        sdg=["4.4", "8.5"],
    ),
    Role(
        "Customer Success Analyst",
        ["crm administration", "data visualisation", "sql"],
        trend=0.2,
        sdg=["8.5", "4.4"],
    ),
    Role(
        "Data Steward",
        ["sql", "excel", "data visualisation"],
        trend=0.1,
        sdg=["9.1", "8.5"],
    ),
    Role(
        "Machine Learning Engineer",
        ["python", "machine learning", "sql"],
        trend=0.9,
        sdg=["9.1", "4.4"],
    ),
]


def main() -> None:
    project = os.getenv("PROJECT_NAME", "SkillRadar MY")
    print(f"== {project} ==")
    print(f"Demo profile: {', '.join(DEMO_PROFILE)}\n")

    for scenario in ("moderate", "fast"):
        print(f"-- scenario: {scenario} --")
        results = rank(DEMO_PROFILE, ROLES, scenario=scenario)
        for r in results[:3]:
            c = r["components"]
            print(
                f"{r['score']:5.1f}  {r['role']:<28} "
                f"coverage={c['coverage']:.2f} transfer={c['transfer']:.2f} "
                f"trend={c['trend']:.2f} gap={c['gap_cost']:.2f}  SDG {','.join(r['sdg'])}"
            )
        top = results[0]
        print(f"  missing: {', '.join(top['missing']) or 'none'}")
        print(f"  pathway: {json.dumps(pathway(top)[:3], ensure_ascii=False)}")
        print()

    print("SDG coverage across shortlist:", sdg_summary(rank(DEMO_PROFILE, ROLES)))


if __name__ == "__main__":
    main()
