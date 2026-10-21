"""Core scoring helpers for SkillRadar MY.

Pure standard library so that `python src/main.py` and the unit tests work
before any third-party dependency is installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math


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

WEIGHTS = {"coverage": 0.30, "focus": 0.25, "transfer": 0.15, "trend": 0.15, "gap": 0.15}


# Modified 2026-10-20: normalize distinct skills and reject malformed records.
def normalize_skills(skills: object) -> list[str]:
    if skills is None:
        return []
    if not isinstance(skills, (list, tuple, set, frozenset)):
        raise ValueError("Skills must be a collection of strings, not text or an object.")
    if any(not isinstance(skill, str) for skill in skills):
        raise ValueError("Every skill must be a string.")
    return sorted({skill.strip().casefold() for skill in skills if skill.strip()})


def match_coverage(profile: object, name: object, required_skills: object) -> dict:
    """Exact, unrounded set coverage; empty role requirements are invalid."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Role name must be non-empty text.")
    known = set(normalize_skills(profile))
    required = normalize_skills(required_skills)
    if not required:
        raise ValueError("A role must require at least one skill.")
    covered = [skill for skill in required if skill in known]
    missing = [skill for skill in required if skill not in known]
    return {"role": name.strip(), "coverage": len(covered) / len(required),
            "covered": covered, "missing": missing, "required_count": len(required)}


def _transfer_score(skill: str, required: str) -> float:
    if skill == required:
        return 1.0
    return TRANSFERABILITY.get((skill, required), 0.0)


def evaluate(profile: list[str], role: Role, scenario: str = "moderate") -> dict:
    """Return an explainable match record for one role.

    score = 0.30*coverage + 0.25*focus + 0.15*transfer + 0.15*trend
            + 0.15*(1 - gap_cost)

    ``focus`` is the share of the user's own skills that this role actually
    needs. Without it a profile with 15 skills covers every role at 100% and
    the ranking stops discriminating.

    ``scenario`` is "moderate" or "fast"; fast disruption doubles the weight
    of the trend signal, which is how the two-scenario view is produced.
    """
    if scenario not in {"moderate", "fast"}:
        raise ValueError("Unknown scenario.")
    if isinstance(role.trend, bool) or not isinstance(role.trend, (int, float)) or not math.isfinite(role.trend) or not -1 <= role.trend <= 1:
        raise ValueError("Simulated trend must be finite and within [-1, 1].")
    profile = normalize_skills(profile)
    matched = match_coverage(profile, role.name, role.required_skills)
    covered, missing = matched["covered"], matched["missing"]
    coverage = matched["coverage"]
    relevant = [s for s in profile if s in {r.strip().lower() for r in role.required_skills}]
    focus = len(relevant) / len(profile) if profile else 0.0
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
        + w["focus"] * focus
        + w["transfer"] * transfer
        + w["trend"] * trend
        + w["gap"] * (1.0 - gap_cost)
    )

    return {
        "role": role.name,
        "score": round(score * 100, 1),
        "components": {
            "coverage": coverage,
            "focus": focus,
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
                "resource": "未接入经核验的课程；周数仅为演示假设",
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
