"""Regression coverage for raw source text versus canonical scoring keys."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from src.trends import validate_snapshot, snapshot_signals, apply_trend, import_snapshot, read_snapshot, update_status
from src.utils import Role, evaluate

ROOT = Path(__file__).resolve().parents[1]

def document(model_skill="python"):
    data = json.loads((ROOT / "data/trends/wef_future_jobs_2025.json").read_text(encoding="utf-8"))
    data["skill_signals"] = [{"skill": "Original Report Category", "model_skill": model_skill,
        "mapping_kind": "proxy", "mapping_note": "Explicit team taxonomy proxy for a synthetic test.",
        "direction": "rising", "evidence": "Synthetic test evidence, not a source statistic."}]
    return data

class TestTrendKeys(unittest.TestCase):
    def test_case_whitespace_and_raw_wording(self):
        scores = []
        for spelling in ["python", "PYTHON", " PYTHON "]:
            raw = document(spelling)
            untouched = copy.deepcopy(raw)
            normalized = validate_snapshot(raw)
            self.assertEqual(raw, untouched)
            row = normalized["skill_signals"][0]
            self.assertEqual(row["skill"], "Original Report Category")
            self.assertEqual(row["model_skill"], spelling)
            self.assertEqual(row["mapping_note"], raw["skill_signals"][0]["mapping_note"])
            self.assertEqual(row["match_key"], "python")
            role = apply_trend([Role("Synthetic role", [" PYTHON ", "python"], .2)], {"signals": snapshot_signals(normalized)})[0]
            scores.append(evaluate(["Python"], role)["score"])
            self.assertGreater(role.trend, .2)
        self.assertEqual(len(set(scores)), 1)

    def test_empty_invalid_and_duplicate_keys(self):
        for value in ["", "   ", None, 12, [], {}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_snapshot(document(value))
        d = document()
        d["skill_signals"].append({**d["skill_signals"][0], "model_skill": " PYTHON "})
        with self.assertRaises(ValueError):
            validate_snapshot(d)
        with self.assertRaises(ValueError):
            apply_trend([Role("r", ["python"], .2)], {"signals": [{"skill": "python", "weight": .7}, {"skill": " PYTHON ", "weight": .7}]})

    def test_context_never_scores_even_when_name_is_known(self):
        d = document()
        d["skill_signals"] = [{"skill": "Python", "mapping_kind": "unmapped", "direction": "rising", "evidence": "Context only"}]
        signals = snapshot_signals(d)
        self.assertIsNone(signals[0]["match_key"])
        self.assertEqual(apply_trend([Role("r", ["python"], .2)], {"signals": signals})[0].trend, .2)
        # A valid source category outside the catalogue is preserved without matching a role.
        d["skill_signals"][0].pop("mapping_kind")
        d["skill_signals"][0]["skill"] = "Unmapped report-only category"
        self.assertEqual(apply_trend([Role("r", ["python"], .2)], {"signals": snapshot_signals(d)})[0].trend, .2)

    def test_import_read_score_and_rejected_update(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            incoming = folder / "incoming.json"
            raw = document(" PYTHON ")
            incoming.write_text(json.dumps(raw), encoding="utf-8")
            import_snapshot("wef", incoming, folder)
            target = folder / "wef_future_jobs_2025.json"
            loaded = read_snapshot(target)
            self.assertEqual(loaded["skill_signals"][0]["model_skill"], " PYTHON ")
            self.assertEqual(loaded["skill_signals"][0]["match_key"], "python")
            self.assertGreater(apply_trend([Role("r", ["python"], .2)], {"signals": snapshot_signals(loaded)})[0].trend, .2)
            good = target.read_bytes()
            raw["skill_signals"][0]["model_skill"] = " "
            incoming.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(ValueError):
                import_snapshot("wef", incoming, folder)
            self.assertEqual(target.read_bytes(), good)
            self.assertFalse(update_status(folder, "wef")["ok"])

    def test_unmapped_conflicts_are_rejected(self):
        d = document()
        d["skill_signals"][0]["mapping_kind"] = "unmapped"
        with self.assertRaises(ValueError):
            validate_snapshot(d)
