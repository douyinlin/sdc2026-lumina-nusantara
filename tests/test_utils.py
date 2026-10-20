"""Unit tests for the SkillRadar scoring engine."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils import Role, evaluate, pathway, rank, sdg_summary  # noqa: E402

ROLE = Role(
    "AI Operations Specialist",
    ["prompt engineering", "data visualisation", "sql", "customer support"],
    trend=0.8,
    sdg=["4.4", "8.5"],
)


class TestScoring(unittest.TestCase):
    def test_full_coverage_scores_high(self):
        result = evaluate(
            ["prompt engineering", "data visualisation", "sql", "customer support"], ROLE
        )
        self.assertGreater(result["score"], 70)
        self.assertEqual(result["missing"], [])

    def test_missing_skills_reported(self):
        result = evaluate(["customer support"], ROLE)
        self.assertIn("sql", result["missing"])
        self.assertEqual(result["components"]["coverage"], 0.25)

    def test_case_and_whitespace_insensitive(self):
        a = evaluate(["SQL", " Customer Support "], ROLE)
        b = evaluate(["sql", "customer support"], ROLE)
        self.assertEqual(a["score"], b["score"])

    def test_fast_scenario_rewards_rising_roles(self):
        declining = Role("Legacy Role", ["excel"], trend=-0.8)
        rising = Role("Rising Role", ["excel"], trend=0.8)
        moderate = {r["role"]: r["score"] for r in rank(["excel"], [declining, rising], "moderate")}
        fast = {r["role"]: r["score"] for r in rank(["excel"], [declining, rising], "fast")}
        self.assertGreater(fast["Rising Role"] - fast["Legacy Role"],
                           moderate["Rising Role"] - moderate["Legacy Role"])

    def test_pathway_orders_cheapest_first(self):
        result = evaluate(["customer support"], ROLE)
        plan = pathway(result)
        self.assertEqual([p["step"] for p in plan], list(range(1, len(plan) + 1)))
        self.assertLessEqual(plan[0]["weeks"], plan[-1]["weeks"])

    def test_sdg_summary_counts(self):
        results = rank(["customer support"], [ROLE, ROLE])
        self.assertEqual(sdg_summary(results)["4.4"], 2)


if __name__ == "__main__":
    unittest.main()
