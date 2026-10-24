"""Regression coverage for applying and reverting a synthetic trend upload."""
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from src.i18n import T
from src.trends import snapshot_signals, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]


class TestTrendSession(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / "data/trends/sample_upload_example.json").read_bytes()
        validated = validate_snapshot(json.loads(self.raw))
        self.snapshot = {
            **validated, "signals": snapshot_signals(validated),
            "observed": True, "forecast": False, "scenario": False,
        }

    def page(self, lang, **state):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        for key, value in {
            "stage": "js_results", "lang": lang, "skills": ["excel", "sql"],
            "persona": "worker", "worker_field": "all", "hours": 8, **state,
        }.items():
            app.session_state[key] = value
        return app

    def healthy_results(self, app, lang):
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0, [e.value for e in app.error])
        for heading in ("p3", "p4"):
            self.assertIn(T(lang)[heading], [h.value for h in app.subheader])
        self.assertEqual(app.session_state["skills"], ["excel", "sql"])
        self.assertEqual(app.session_state["hours"], 8)

    def upload(self, *args, **kwargs):
        file = io.BytesIO(self.raw)
        file.name = "sample_upload_example.json"
        file.size = len(self.raw)
        return file

    def test_apply_upload_keeps_complete_results_in_all_languages(self):
        for lang in ("en", "zh", "ms"):
            with self.subTest(lang=lang), patch("streamlit.file_uploader", side_effect=self.upload):
                app = self.page(lang).run()
                self.healthy_results(app, lang)
                app.button(key="trend_apply").click().run()
                self.healthy_results(app, lang)
                self.assertEqual(app.session_state["trend_source"], "session")
                self.assertEqual(app.session_state["trend_session_snapshot"], self.snapshot)
                self.assertIn(T(lang)["src_note_session"], [c.value for c in app.caption])
                app.run()
                self.healthy_results(app, lang)
                self.assertEqual(app.session_state["trend_source"], "session")
                app.radio(key="trend_source").set_value("jobstreet").run()
                self.healthy_results(app, lang)
                self.assertEqual(app.session_state["trend_source"], "jobstreet")

    def test_revert_restores_wef_without_reactivating_session(self):
        for lang in ("en", "zh", "ms"):
            for source in ("session", "wef"):
                with self.subTest(lang=lang, source=source):
                    app = self.page(lang, trend_session_snapshot=self.snapshot, trend_source=source).run()
                    self.healthy_results(app, lang)
                    app.button(key="trend_revert").click().run()
                    self.healthy_results(app, lang)
                    self.assertNotIn("trend_session_snapshot", app.session_state)
                    self.assertEqual(app.session_state["trend_source"], "wef")
                    self.assertNotIn(T(lang)["src_session"], app.radio(key="trend_source").options)
                    self.assertFalse(any(b.key == "trend_revert" for b in app.button))
                    app.run()
                    self.healthy_results(app, lang)
                    self.assertEqual(app.session_state["trend_source"], "wef")
