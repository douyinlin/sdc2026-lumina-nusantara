"""Check actual disclosures rather than only translation-key presence."""
import json
from pathlib import Path
import unittest
from src.i18n import T

ROOT = Path(__file__).resolve().parents[1]

class TestCopyConsistency(unittest.TestCase):
    def test_course_disclosure_matches_visible_note(self):
        forbidden = ["HRD Corp", "provider's estimate", "真实可访问", "时长为提供方", "sumber sebenar yang boleh diakses"]
        for lang in ["en", "zh", "ms"]:
            t = T(lang)
            self.assertIn(t["courses_note"], t["disclose_body"])
            for phrase in forbidden:
                self.assertNotIn(phrase, t["courses_note"] + t["disclose_body"])
            self.assertIn(t["courses_note"], (ROOT / "src/i18n.py").read_text(encoding="utf-8"))

    def test_provenance_and_rule_claims(self):
        tokens = {"en": ["not been reverified", "team estimates"], "zh": ["未重新核实", "团队估算"], "ms": ["belum disahkan semula", "anggaran pasukan"]}
        for lang, phrases in tokens.items():
            t = T(lang)
            for phrase in phrases:
                self.assertIn(phrase, t["courses_note"])
            self.assertNotIn("Verified learning resources", t["courses_title"])
            self.assertNotIn("已核实", t["courses_title"])
            self.assertTrue(t["duration_verified"] and t["duration_catalogue"] and t["duration_team"])
            self.assertIn({"en":"team rule coefficient", "zh":"团队规则系数", "ms":"pekali aturan pasukan"}[lang], t["why_transfer_item"])
            self.assertTrue(t["coverage_disclaimer"] and t["impact_note"])
        catalogue = json.loads((ROOT / "data/courses.json").read_text(encoding="utf-8"))
        self.assertEqual(catalogue["verification_status"], "pending_team_review")
