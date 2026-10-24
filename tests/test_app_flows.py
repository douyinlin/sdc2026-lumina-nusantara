"""Streamlit integration tests; synthetic profiles only, no external requests."""
from pathlib import Path
import unittest
from unittest.mock import patch
from src.i18n import T
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

def run_page(stage, lang="en", **state):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    app.session_state["stage"] = stage
    app.session_state["lang"] = lang
    for key, value in state.items():
        app.session_state[key] = value
    return app.run()

def persona_radio(app):
    """Persona is the two-option radio; theme and text-size pickers add their own radios."""
    return next(r for r in app.radio if len(list(r.options)) == 2)


def choose_persona(app, index=1):
    radio = persona_radio(app)
    radio.set_value(list(radio.options)[index]).run()
    return app


class TestAppFlows(unittest.TestCase):
    def healthy(self, app):
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)

    def test_locales_and_personas(self):
        for lang in ["en", "zh", "ms"]:
            cases = [("js_results", {"skills": ["sql", "python"], "persona": "worker", "worker_field": "all", "hours": 8}),
                     ("js_results", {"skills": ["sql"], "persona": "grad", "graduate_field": "Computer Science", "hours": 10}),
                     ("hr_results", {"roster": {"AI Operations Specialist": 2}}),
                     ("cc_results", {"targets": ["AI Operations Specialist"], "taught": ["sql"], "prog": "Fictional programme", "cohort": 10})]
            for stage, state in cases:
                with self.subTest(lang=lang, stage=stage, persona=state.get("persona")):
                    self.healthy(run_page(stage, lang, **state))

    def test_inputs_source_and_learning_time(self):
        app = run_page("js_intake", graduate_field="Computer Science")
        self.healthy(app)
        self.assertEqual(app.session_state["worker_field"], "all")
        self.assertEqual(app.session_state["graduate_field"], "Computer Science")
        app.selectbox(key="worker_field_widget").set_value("Computer Science").run()
        self.healthy(app)
        self.assertEqual(app.session_state["worker_field"], "Computer Science")
        choose_persona(app)
        self.healthy(app)
        self.assertEqual(app.session_state["graduate_field"], "Computer Science")
        self.assertEqual(app.session_state["worker_field"], "Computer Science")
        app = run_page("js_results", skills=["sql"], persona="worker", worker_field="Computer Science", hours=8)
        self.healthy(app)
        before = [m.value for m in app.metric]
        app.session_state["hours"] = 16
        app.run()
        self.healthy(app)
        self.assertNotEqual(before, [m.value for m in app.metric])
        app.radio(key="trend_source").set_value("jobstreet").run()
        self.healthy(app)
        app.session_state["skills"] = ["sql", "python", "machine learning"]
        app.run()
        self.healthy(app)

    def test_import_failure_warning_is_visible(self):
        with patch("src.trends.update_status", return_value={"ok": False}):
            app = run_page("js_results", skills=["sql"], persona="worker", worker_field="all", hours=8)
        self.healthy(app)
        self.assertIn(T("en")["update_failed"], [warning.value for warning in app.warning])

    def test_intake_locales(self):
        for lang in ["en", "zh", "ms"]:
            for stage in ["js_intake", "hr_intake", "cc_intake"]:
                with self.subTest(lang=lang, stage=stage):
                    app = run_page(stage, lang)
                    self.healthy(app)
                    if stage == "js_intake":
                        choose_persona(app)
                        self.healthy(app)
