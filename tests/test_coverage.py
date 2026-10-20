"""Core coverage invariants and invalid-catalogue regression tests."""
import json
import tempfile
import unittest
from pathlib import Path

from src.demo import compare_skills, load_demo
from src.utils import match_coverage, evaluate, Role


class TestCoverage(unittest.TestCase):
    def test_deduplicates_both_sides_and_normalizes(self):
        result = match_coverage([" SQL ", "sql", "EXCEL", ""], "Demo", ["sql", "SQL", "excel", "python", " "])
        self.assertEqual(result["coverage"], 2 / 3)
        self.assertEqual(result["covered"], ["excel", "sql"])
        self.assertEqual(result["missing"], ["python"])
        self.assertEqual(result["required_count"], 3)

    def test_empty_and_full_input(self):
        self.assertEqual(match_coverage([], "Demo", ["sql"])["coverage"], 0)
        self.assertEqual(match_coverage(None, "Demo", ["sql"])["coverage"], 0)
        self.assertEqual(match_coverage(["sql"], "Demo", ["sql"])["coverage"], 1)

    def test_invalid_input(self):
        for value in ("sql", {"sql": True}, 1, [None], [4]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                match_coverage(value, "Demo", ["sql"])

    def test_invalid_role(self):
        for name, skills in (("", ["sql"]), (None, ["sql"]), ("Demo", []), ("Demo", [" "]), ("Demo", "sql")):
            with self.subTest(name=name, skills=skills), self.assertRaises(ValueError):
                match_coverage([], name, skills)

    def test_demo_results_change_after_edit(self):
        data = load_demo()
        before = compare_skills(data["profile"]["skills"], data)
        after = compare_skills(["excel", "communication", "sql"], data)
        self.assertEqual([r["coverage"] for r in before], [1 / 4, 2 / 3, 0])
        self.assertEqual([r["coverage"] for r in after], [1 / 2, 2 / 3, 1 / 3])
        self.assertEqual([r["coverage"] for r in compare_skills([], data)], [0, 0, 0])
        with self.assertRaises(ValueError):
            compare_skills(["invented"], data)

    def test_malformed_catalogue(self):
        for mutate in (lambda d: d.update(is_simulated=False), lambda d: d["roles"][0].update(required_skills=[]), lambda d: d["roles"][0].update(required_skills=["invented"]), lambda d: d["roles"].append(d["roles"][0])):
            data = load_demo()
            mutate(data)
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "demo.json"
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_demo(path)

    def test_experimental_validation(self):
        for trend in (float("nan"), float("inf"), 2, "high", True):
            with self.subTest(trend=trend), self.assertRaises(ValueError):
                evaluate([], Role("Demo", ["sql"], trend))
        with self.assertRaises(ValueError):
            evaluate([], Role("Demo", ["sql"], 0), "unknown")


if __name__ == "__main__":
    unittest.main()
