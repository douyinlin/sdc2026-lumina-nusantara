"""Guard: every copy key the app reads must exist in all three languages.

A missing key does not fail locally until that exact screen renders, which is how
a redeploy shipped a `KeyError` to the live demo. This test reads app.py instead,
so the mistake is caught before pushing.
"""
import json
import re
import unittest
from pathlib import Path

from src.i18n import ROLE_PARENTHETICAL, SKILL_PARENTHETICAL, STRINGS

APP = Path(__file__).resolve().parents[1] / "app.py"
ROLES = Path(__file__).resolve().parents[1] / "data" / "roles.json"
LANGS = ("en", "zh", "ms")

# keys assembled at runtime, so the regex cannot see them
DYNAMIC = [
    "src_dosm", "src_jobstreet", "src_badge_obs", "src_badge_scenario",
    "moderate", "fast",
]


class TestCopyKeys(unittest.TestCase):
    def test_literal_keys_exist_in_every_language(self):
        source = APP.read_text(encoding="utf-8")
        keys = sorted(set(re.findall(r'\bt\["([a-z0-9_]+)"\]', source)))
        for lang in LANGS:
            missing = [k for k in keys if k not in STRINGS[lang]]
            with self.subTest(lang=lang):
                self.assertEqual(missing, [], f"{lang} is missing: {missing}")

    def test_runtime_keys_exist(self):
        for lang in LANGS:
            for key in DYNAMIC:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, STRINGS[lang])

    def test_decision_copy_merged(self):
        # the trend-source layer lives in its own module; if the merge breaks,
        # the results page dies on its first key
        for lang in LANGS:
            for key in ("src_label", "robust_title", "why_title", "bridge_title",
                        "impact_gap", "path_evidence", "both_title", "summary_full",
                        "ev_line", "named_area", "scen_compare"):
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, STRINGS[lang])

    def test_every_role_is_named_in_chinese_and_malay(self):
        # an untranslated role shows up as bare English in the middle of 中文 UI
        data = json.loads(ROLES.read_text(encoding="utf-8"))
        roles = data["roles"] if isinstance(data, dict) else data
        for lang in ("zh", "ms"):
            missing = [r["name"] for r in roles if r["name"] not in ROLE_PARENTHETICAL.get(lang, {})]
            with self.subTest(lang=lang):
                self.assertEqual(missing, [], f"untranslated roles: {missing}")

    def test_every_catalogue_skill_has_a_gloss(self):
        data = json.loads(ROLES.read_text(encoding="utf-8"))
        roles = data["roles"] if isinstance(data, dict) else data
        skills = sorted({s for r in roles for s in r.get("required_skills", [])})
        for lang in ("zh", "ms"):
            missing = [s for s in skills if s not in SKILL_PARENTHETICAL.get(lang, {})]
            with self.subTest(lang=lang):
                self.assertEqual(missing, [], f"skills without a gloss: {missing}")


if __name__ == "__main__":
    unittest.main()
