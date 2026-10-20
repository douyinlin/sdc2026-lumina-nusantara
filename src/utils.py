"""Core scoring helpers for SkillRadar MY.

Pure standard library so that `python src/main.py` and the unit tests work
before any third-party dependency is installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Role:
    """A candidate future role."""

    name: str
    required_skills: list[str]
    trend: float  # -1.0 (declining) .. +1.0 (rising)
    sdg: list[str] = field(default_factory=list)


#: How easily one skill transfers into another (0..1).
TRANSFERABILITY = {
    ("excel", "sql"): 0.6,
    ("excel", "data visualisation"): 0.7,
    ("customer support", "crm administration"): 0.8,
    ("customer support", "prompt engineering"): 0.3,
    ("python", "sql"): 0.5,
    ("python", "machine learning"): 0.4,
    ("project management", "product management"): 0.6,
}

#: Relative cost of closing a gap, by skill family (lower is cheaper).
GAP_COST = {
    "prompt engineering": 0.3,
    "data visualisation": 0.4,
    "sql": 0.5,
    "crm administration": 0.4,
    "machine learning": 0.9,
    "product management": 0.8,
}

WEIGHTS = {"coverage": 0.40, "transfer": 0.25, "trend": 0.20, "gap": 0.15}


def _transfer_score(skill: str, required: str) -> float:
    if skill == required:
        return 1.0
    return TRANSFERABILITY.get((skill, required), 0.0)


def evaluate(profile: list[str], role: Role, scenario: str = "moderate") -> dict:
    """Return an explainable match record for one role.

    score = 0.40*coverage + 0.25*transfer + 0.20*trend + 0.15*(1 - gap_cost)

    ``scenario`` is "moderate" or "fast"; fast disruption doubles the weight
    of the trend signal, which is how the two-scenario view is produced.
    """
    profile = [s.strip().lower() for s in profile]
    required = [s.strip().lower() for s in role.required_skills]

    covered = [s for s in required if s in profile]
    missing = [s for s in required if s not in profile]

    coverage = len(covered) / len(required) if required else 0.0
    transfer = (
        max((_transfer_score(p, r) for p in profile for r in missing), default=0.0)
        if missing
        else 1.0
    )
    trend = (role.trend + 1.0) / 2.0  # map -1..1 -> 0..1

    gap_cost = (
        sum(GAP_COST.get(s, 0.7) for s in missing) / len(missing) if missing else 0.0
    )

    w = dict(WEIGHTS)
    if scenario == "fast":
        w["trend"] *= 2.0
        total_w = sum(w.values())
        w = {k: v / total_w for k, v in w.items()}

    score = (
        w["coverage"] * coverage
        + w["transfer"] * transfer
        + w["trend"] * trend
        + w["gap"] * (1.0 - gap_cost)
    )

    return {
        "role": role.name,
        "score": round(score * 100, 1),
        "components": {
            "coverage": round(coverage, 2),
            "transfer": round(transfer, 2),
            "trend": round(trend, 2),
            "gap_cost": round(gap_cost, 2),
        },
        "covered": covered,
        "missing": missing,
        "sdg": role.sdg,
    }


def rank(profile: list[str], roles: list[Role], scenario: str = "moderate") -> list[dict]:
    """Rank roles best-first for a profile under a given scenario."""
    results = [evaluate(profile, r, scenario) for r in roles]
    return sorted(results, key=lambda r: r["score"], reverse=True)


def pathway(result: dict) -> list[dict]:
    """Order the missing skills of a match into a learning plan.

    Cheapest-first (highest transferability, lowest gap cost first) so the
    learner gets a quick win before the expensive modules.
    """
    plan = []
    for i, skill in enumerate(sorted(result["missing"], key=lambda s: GAP_COST.get(s, 0.7)), start=1):
        plan.append(
            {
                "step": i,
                "skill": skill,
                "weeks": max(1, round(GAP_COST.get(skill, 0.7) * 6)),
                "resource": f"https://www.hrdcorp.gov.my/ (search: {skill})",
            }
        )
    return plan


def sdg_summary(results: list[dict]) -> dict[str, int]:
    """Count SDG tags across a ranked shortlist."""
    counts: dict[str, int] = {}
    for r in results:
        for tag in r["sdg"]:
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
