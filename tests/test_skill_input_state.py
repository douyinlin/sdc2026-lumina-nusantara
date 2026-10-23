"""Exercise actual Streamlit controls with a synthetic file uploader boundary."""
import io
from pathlib import Path
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from src.cv import cv_to_skills
from src.i18n import T

ROOT = Path(__file__).resolve().parents[1]

class TestSkillInputState(unittest.TestCase):
    def setUp(self):
        self.content = b"Fictional profile: SQL"
        def upload(*args, **kwargs):
            f = io.BytesIO(self.content)
            f.name = "same-name.txt"
            return f
        self.upload_patch = patch("streamlit.file_uploader", side_effect=upload)
        self.upload_patch.start()
        self.addCleanup(self.upload_patch.stop)
        self.parser_patch = patch("src.cv.cv_to_skills", wraps=cv_to_skills)
        self.parser = self.parser_patch.start()
        self.addCleanup(self.parser_patch.stop)

    def page(self, lang="en"):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        app.session_state["stage"] = "js_intake"
        app.session_state["lang"] = lang
        return app.run()

    def button(self, app, key, lang="en"):
        return next(b for b in app.button if b.label == T(lang)[key])

    def healthy(self, app):
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)

    def test_upload_edit_continue_all_languages(self):
        for lang in ["en", "zh", "ms"]:
            with self.subTest(lang=lang):
                app = self.page(lang)
                app.multiselect(key="ms_📊 Office & Data").select("Excel / spreadsheets").run()
                self.button(app, "use_skills", lang).click().run()
                self.assertEqual(app.session_state["skills"], ["excel"])
                next(n for n in app.number_input if n.label == T(lang)["q_hours"]).set_value(12).run()
                self.assertEqual(app.session_state["skills"], ["excel"])
                self.button(app, "continue", lang).click().run()
                self.healthy(app)
                self.assertEqual(app.session_state["stage"], "js_results")
                self.assertEqual(app.session_state["skills"], ["excel"])
                self.assertIn(T(lang)["p3"], [h.value for h in app.subheader])
        self.assertEqual(self.parser.call_count, 3)

    def test_clear_with_upload_retained_and_new_same_name_content(self):
        app = self.page()
        self.button(app, "clear_skills").click().run()
        self.assertEqual(app.session_state["skills"], [])
        self.assertTrue(self.button(app, "continue").disabled)
        app.run()
        self.assertEqual(app.session_state["skills"], [])
        self.assertEqual(self.parser.call_count, 1)
        self.content = b"Fictional profile: Python"
        app.run()
        self.healthy(app)
        self.assertEqual(app.session_state["skills"], ["python"])
        self.assertFalse(self.button(app, "continue").disabled)
        self.assertEqual(self.parser.call_count, 2)

    def test_search_and_category_share_draft_and_can_apply_empty(self):
        app = self.page()
        self.assertTrue(self.button(app, "use_skills").disabled)
        app.text_input(key="skill_query").set_value("Excel").run()
        app.multiselect(key="skill_search_pick").select("Excel / spreadsheets").run()
        self.assertEqual(app.multiselect(key="ms_📊 Office & Data").value, ["Excel / spreadsheets"])
        self.button(app, "use_skills").click().run()
        self.assertEqual(app.session_state["skills"], ["excel"])
        app.multiselect(key="ms_📊 Office & Data").unselect("Excel / spreadsheets").run()
        self.assertEqual(app.multiselect(key="skill_search_pick").value, [])
        self.button(app, "use_skills").click().run()
        self.assertEqual(app.session_state["skills"], [])
        self.assertTrue(self.button(app, "continue").disabled)
        app.run()
        self.assertEqual(app.session_state["skills"], [])

    def test_explicit_clear_clears_all_widget_choices(self):
        app = self.page()
        app.text_input(key="skill_query").set_value("Excel").run()
        app.multiselect(key="skill_search_pick").select("Excel / spreadsheets").run()
        self.button(app, "clear_skills").click().run()
        self.healthy(app)
        self.assertEqual(app.text_input(key="skill_query").value, "")
        self.assertTrue(all(not m.value for m in app.multiselect))
        self.assertTrue(self.button(app, "use_skills").disabled)
        self.assertTrue(self.button(app, "continue").disabled)
