"""Guard: every copy key the app reads must exist in all three languages.

A missing key does not fail locally until that exact screen renders, which is how
a redeploy shipped a `KeyError` to the live demo. This test reads app.py instead,
so the mistake is caught before pushing.
"""
import re
import unittest
from pathlib import Path

from src.i18n import STRINGS

APP = Path(__file__).resolve().parents[1] / "app.py"
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
                        "impact_gap", "path_evidence", "both_title"):
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, STRINGS[lang])


if __name__ == "__main__":
    unittest.main()
