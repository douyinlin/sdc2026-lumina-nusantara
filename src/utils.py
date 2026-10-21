"""Core scoring helpers for SkillRadar MY.

Pure standard library so that `python src/main.py` and the unit tests work
before any third-party dependency is installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math


SKILL_TIER_WEIGHT = {"core": 1.0, "important": 0.6, "nice": 0.3}

# Per-skill cost of closing the gap (higher = harder / longer).
SKILL_GAP_COST = {
    "prompt engineering": 0.30, "data visualisation": 0.35, "excel": 0.25,
    "sql": 0.45, "crm administration": 0.30, "reporting": 0.25,
    "customer support": 0.20, "communication": 0.20, "basic statistics": 0.45,
    "python": 0.55, "machine learning": 0.85, "cloud": 0.70, "cybersecurity": 0.75,
    "web development": 0.60, "ui ux": 0.55, "graphic design": 0.45,
    "research": 0.40, "project management": 0.50, "product management": 0.60,
    "team lead": 0.50, "hr operations": 0.35, "recruitment": 0.40,
    "negotiation": 0.40, "presentation": 0.25, "coaching": 0.40,
    "financial modelling": 0.65, "financial reporting": 0.60, "bookkeeping": 0.40,
    "contract review": 0.65, "compliance": 0.55, "documentation": 0.25,
    "quality assurance": 0.40, "lean": 0.60, "osh": 0.50,
    "machine operation": 0.55, "logistics": 0.35, "inventory": 0.30,
    "data entry": 0.20, "clinic admin": 0.35, "patient care": 0.55,
    "counselling": 0.60, "teaching": 0.60, "content": 0.30, "copywriting": 0.35,
    "digital marketing": 0.45, "video editing": 0.40, "automation": 0.55,
    "process improvement": 0.45, "stakeholder management": 0.45,
    "supply chain": 0.50, "research": 0.40,
}


@dataclass
class Role:
    """A candidate future role."""

    name: str
    required_skills: list[str]
    trend: float  # -1.0 (declining) .. +1.0 (rising)
    sdg: list[str] = field(default_factory=list)
    # optional: {"skill": "core" | "important" | "nice"}; empty = all "important"
    tiers: dict[str, str] = field(default_factory=dict)

    def tier_of(self, skill: str) -> str:
        return self.tiers.get(skill.strip().lower(), "important")


#: How easily one skill transfers into another (0..1).
TRANSFERABILITY = {
    # office / data
    ("excel", "sql"): 0.6,
    ("excel", "data visualisation"): 0.7,
    ("excel", "reporting"): 0.8,
    ("excel", "basic statistics"): 0.5,
    ("excel", "financial modelling"): 0.5,
    ("excel", "bookkeeping"): 0.4,
    ("sql", "python"): 0.5,
    ("sql", "data visualisation"): 0.6,
    ("data visualisation", "sql"): 0.5,
    ("data visualisation", "reporting"): 0.8,
    ("data visualisation", "basic statistics"): 0.6,
    ("reporting", "data visualisation"): 0.7,
    ("reporting", "documentation"): 0.6,
    ("basic statistics", "data visualisation"): 0.6,
    ("basic statistics", "research"): 0.7,
    # tech
    ("python", "machine learning"): 0.4,
    ("python", "sql"): 0.5,
    ("python", "automation"): 0.7,
    ("python", "web development"): 0.6,
    ("web development", "ui ux"): 0.5,
    ("machine learning", "python"): 0.6,
    ("machine learning", "basic statistics"): 0.6,
    ("cloud", "it support"): 0.6,
    ("it support", "cloud"): 0.5,
    ("it support", "cybersecurity"): 0.4,
    ("cybersecurity", "compliance"): 0.5,
    ("prompt engineering", "automation"): 0.5,
    ("automation", "process improvement"): 0.7,
    # customer / operations
    ("customer support", "crm administration"): 0.8,
    ("customer support", "communication"): 0.8,
    ("crm administration", "customer support"): 0.7,
    ("crm administration", "data visualisation"): 0.4,
    ("process improvement", "lean"): 0.7,
    ("lean", "process improvement"): 0.7,
    ("lean", "quality assurance"): 0.6,
    ("quality assurance", "documentation"): 0.7,
    ("quality assurance", "compliance"): 0.5,
    ("logistics", "inventory"): 0.8,
    ("inventory", "logistics"): 0.8,
    ("inventory", "excel"): 0.6,
    # people / management
    ("team lead", "project management"): 0.7,
    ("team lead", "coaching"): 0.8,
    ("team lead", "communication"): 0.7,
    ("project management", "product management"): 0.6,
    ("project management", "stakeholder management"): 0.7,
    ("product management", "project management"): 0.6,
    ("coaching", "teaching"): 0.7,
    ("coaching", "counselling"): 0.5,
    ("recruitment", "hr operations"): 0.6,
    ("hr operations", "recruitment"): 0.5,
    # communication & design
    ("communication", "presentation"): 0.8,
    ("communication", "negotiation"): 0.7,
    ("communication", "customer support"): 0.7,
    ("presentation", "teaching"): 0.7,
    ("presentation", "content"): 0.5,
    ("graphic design", "ui ux"): 0.6,
    ("graphic design", "content"): 0.6,
    ("ui ux", "graphic design"): 0.6,
    ("ui ux", "research"): 0.5,
    ("video editing", "content"): 0.7,
    ("content", "copywriting"): 0.7,
    ("content", "digital marketing"): 0.6,
    ("copywriting", "content"): 0.7,
    ("digital marketing", "content"): 0.6,
    # health
    ("patient care", "counselling"): 0.6,
    ("patient care", "clinic admin"): 0.6,
    ("clinic admin", "documentation"): 0.8,
    ("clinic admin", "data entry"): 0.7,
    ("counselling", "communication"): 0.7,
    # legal / finance
    ("contract review", "compliance"): 0.6,
    ("compliance", "documentation"): 0.6,
    ("financial reporting", "bookkeeping"): 0.7,
    ("financial modelling", "financial reporting"): 0.6,
    ("bookkeeping", "financial reporting"): 0.7,
    # science
    ("research", "reporting"): 0.7,
    ("research", "quality assurance"): 0.5,
    # hospitality
    ("customer support", "team lead"): 0.5,
    ("logistics", "excel"): 0.5,
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

# "fast" disruption: demand trend dominates and volatile roles swing harder.
WEIGHTS_FAST = {"coverage": 0.24, "focus": 0.18, "transfer": 0.11, "trend": 0.35, "gap": 0.12}
TREND_AMPLIFY_FAST = 1.8
GAP_DISCOUNT_FAST = 0.7
FAST_FLAT_PENALTY = 0.20      # flat roles are crowded out when disruption accelerates
FAST_DECLINE_PENALTY = 0.40   # declining roles lose real ground


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

    ``coverage`` is now weighted by skill importance: a core skill counts 1.0,
    an important one 0.6 and a nice-to-have 0.3, so two roles that each miss two
    skills no longer score identically. ``transfer`` is also weighted and counts
    *how much of the missing requirement* existing skills can carry, instead of
    taking the single best skill pair.
    """
    if scenario not in {"moderate", "fast"}:
        raise ValueError("Unknown scenario.")
    if isinstance(role.trend, bool) or not isinstance(role.trend, (int, float)) or not math.isfinite(role.trend) or not -1 <= role.trend <= 1:
        raise ValueError("Simulated trend must be finite and within [-1, 1].")

    profile = normalize_skills(profile)
    matched = match_coverage(profile, role.name, role.required_skills)
    covered, missing = matched["covered"], matched["missing"]

    required = [s.strip().lower() for s in role.required_skills]
    total_weight = sum(SKILL_TIER_WEIGHT[role.tier_of(s)] for s in required) or 1.0
    covered_weight = sum(SKILL_TIER_WEIGHT[role.tier_of(s)] for s in covered)
    coverage = covered_weight / total_weight

    # focus: share of the user's own skills this role actually needs
    relevant = [s for s in profile if s in set(required)]
    focus = len(relevant) / len(profile) if profile else 0.0

    # weighted transferability: how much of the missing requirement existing skills can carry
    if missing:
        missing_weight = sum(SKILL_TIER_WEIGHT[role.tier_of(s)] for s in missing) or 1.0
        carried = 0.0
        for gap in missing:
            best = max((_transfer_score(p, gap) for p in profile), default=0.0)
            carried += SKILL_TIER_WEIGHT[role.tier_of(gap)] * best
        transfer = carried / missing_weight
    else:
        transfer = 1.0

    trend = (role.trend + 1.0) / 2.0

    # per-skill gap cost, weighted by importance
    if missing:
        gap_cost = sum(
            SKILL_TIER_WEIGHT[role.tier_of(s)] * SKILL_GAP_COST.get(s, 0.5) for s in missing
        ) / (sum(SKILL_TIER_WEIGHT[role.tier_of(s)] for s in missing) or 1.0)
    else:
        gap_cost = 0.0

    if scenario == "fast":
        # a fast-moving market rewards rising roles and punishes flat/declining ones
        if role.trend > 0:
            trend = min(1.0, 0.5 + (trend - 0.5) * TREND_AMPLIFY_FAST)
        elif role.trend == 0:
            trend = max(0.0, 0.5 - FAST_FLAT_PENALTY)          # stalling roles lose ground
        else:
            trend = max(0.0, 0.5 - FAST_DECLINE_PENALTY)
        gap_cost = gap_cost * GAP_DISCOUNT_FAST

    w = dict(WEIGHTS_FAST) if scenario == "fast" else dict(WEIGHTS)

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
            "transfer": transfer,
            "trend": trend,
            "gap_cost": gap_cost,
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
