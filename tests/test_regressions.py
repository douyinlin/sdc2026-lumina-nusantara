import copy
import json
from pathlib import Path
import tempfile
import unittest
from src.utils import Role, evaluate, rank
from src.planning import filter_roles, learning_duration
from src.trends import read_snapshot, import_snapshot, update_status, apply_trend

ROOT = Path(__file__).resolve().parents[1]

class TestRegression(unittest.TestCase):
    def test_duplicate_requirements_and_profile(self):
        r = Role("Role", [" SQL ", "sql", "SQL", "python", ""], 0, tiers={"SQL": "core", "python": "nice"})
        a = evaluate(["SQL", " sql "], r)
        self.assertEqual(a["coverage"], .5)
        self.assertAlmostEqual(a["components"]["coverage"], 1 / 1.3)
        self.assertEqual(evaluate(["sql", "python"], r)["components"]["coverage"], 1)
        self.assertEqual(evaluate([], r)["coverage"], 0)
        self.assertEqual(evaluate(["sql"], Role("r", ["sql", "SQL"], 0))["components"]["coverage"], 1)

    def test_invalid_inputs(self):
        for required in [[], [" "], [None], "sql"]:
            with self.assertRaises(ValueError):
                evaluate([], Role("r", required, 0))
        for profile in ["sql", [None], {"sql": True}]:
            with self.assertRaises(ValueError):
                evaluate(profile, Role("r", ["sql"], 0))
        with self.assertRaises(ValueError):
            evaluate([], Role("r", ["sql"], 0, tiers={"sql": "unknown"}))

    def test_worker_unrestricted_and_grad_filter(self):
        roles = [Role("Tech", ["python", "sql"], 0), Role("Business", ["excel"], 0)]
        meta = {"Tech": {"domain": "it"}, "Business": {"domain": "business"}}
        fields = {"Computing": "it", "Business": "business"}
        selected = filter_roles(roles, meta, "worker", "all", fields, {})
        self.assertEqual(rank(["python", "sql"], selected)[0]["role"], "Tech")
        self.assertEqual([r.name for r in filter_roles(roles, meta, "grad", "Business", fields, {})], ["Business"])

    def test_duration_and_missing_hours(self):
        courses = {"python": {"hours": 90}}
        self.assertEqual(learning_duration("python", courses, 8)["weeks"], 12)
        self.assertEqual(learning_duration("python", courses, 16)["weeks"], 6)
        self.assertEqual(learning_duration("python", courses, 8)["basis"], "duration_catalogue")
        self.assertEqual(learning_duration("sql", courses, 8)["basis"], "duration_team")
        courses["python"].update(duration_verified=True, duration_source_url="https://example.org/course")
        self.assertEqual(learning_duration("python", courses, 8)["basis"], "duration_verified")
        for hours in [0, -1, float("nan"), True]:
            with self.assertRaises(ValueError):
                learning_duration("python", courses, hours)

    def test_import_failure_preserves_previous(self):
        original = read_snapshot(ROOT / "data/trends/wef_future_jobs_2025.json")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            target = folder / "wef_future_jobs_2025.json"
            target.write_text(json.dumps(original), encoding="utf-8")
            previous = target.read_bytes()
            incoming = folder / "incoming.json"
            incoming.write_text('{"skill_signals": []}', encoding="utf-8")
            with self.assertRaises(ValueError):
                import_snapshot("wef", incoming, folder)
            self.assertEqual(target.read_bytes(), previous)
            self.assertFalse(update_status(folder, "wef")["ok"])
            updated = copy.deepcopy(original)
            updated["retrieved_at"] = "2026-10-22"
            incoming.write_text(json.dumps(updated), encoding="utf-8")
            import_snapshot("wef", incoming, folder)
            self.assertTrue(update_status(folder, "wef")["ok"])
            self.assertEqual(read_snapshot(target), updated)
            self.assertEqual(read_snapshot(target.with_suffix(".json.bak")), original)

    def test_signal_changes_score_not_unrelated_role(self):
        roles = [Role("Tech", ["python"], .2), Role("Office", ["excel"], .3)]
        up = apply_trend(roles, {"signals": [{"skill": "python", "weight": .7}]})
        down = apply_trend(roles, {"signals": [{"skill": "python", "weight": -.7}]})
        self.assertGreater(evaluate(["python"], up[0])["score"], evaluate(["python"], down[0])["score"])
        self.assertEqual(up[1].trend, .3)
