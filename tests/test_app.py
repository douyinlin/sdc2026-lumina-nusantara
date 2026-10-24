"""Smoke checks for the current guided UI, not the retired demo screen."""
import logging
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.i18n import T

ROOT = Path(__file__).resolve().parents[1]


class TestGuidedApp(unittest.TestCase):
    def assert_healthy(self, app):
        self.assertEqual(list(app.exception), [])
        self.assertEqual(list(app.error), [])

    def click(self, app, label):
        next(button for button in app.button if button.label == label).click().run()
        self.assert_healthy(app)

    def start(self, lang):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assert_healthy(app)
        app.button(key="intro_zoom_continue").click().run()
        next(s for s in app.selectbox if s.label == "Language / Bahasa / 语言").select(lang).run()
        self.assertEqual(app.session_state["lang"], lang)
        self.assert_healthy(app)
        return app

    def test_languages_and_jobseeker_navigation(self):
        for lang in ("en", "ms", "zh"):
            with self.subTest(lang=lang):
                app = self.start(lang)
                t = T(lang)
                self.click(app, t["p1_btn"])
                self.assertEqual(app.session_state["stage"], "js_intake")
                # A profile without selected skills must not advance.
                self.assertTrue(next(b for b in app.button if b.label == t["continue"]).disabled)
                app.multiselect(key="ms_📊 Office & Data").select("SQL & databases").run()
                self.click(app, t["use_skills"])
                self.click(app, t["continue"])
                self.assertEqual(app.session_state["stage"], "js_results")
                self.assertGreater(len(app.metric), 0)
                self.click(app, t["reeval"])
                self.assertEqual(app.session_state["stage"], "landing")

    def test_hr_and_career_centre_navigation(self):
        for lang in ("en", "ms", "zh"):
            for persona, intake, action, result in (
                ("p2_btn", "hr_intake", "analyse", "hr_results"),
                ("p3_btn", "cc_intake", "cc_run", "cc_results"),
            ):
                with self.subTest(lang=lang, persona=persona):
                    app = self.start(lang)
                    t = T(lang)
                    self.click(app, t[persona])
                    self.assertEqual(app.session_state["stage"], intake)
                    self.click(app, t[action])
                    self.assertEqual(app.session_state["stage"], result)
                    self.assertGreater(len(app.metric), 0)


if __name__ == "__main__":
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    unittest.main()
