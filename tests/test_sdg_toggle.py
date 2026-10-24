"""Keep the SDG button's visual state aligned with its expanded content."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from src.i18n import T


class TestSdgToggle(unittest.TestCase):
    def test_label_and_content_toggle_together(self):
        root = Path(__file__).resolve().parents[1]
        app = AppTest.from_file(str(root / "app.py"), default_timeout=20)
        app.session_state["stage"] = "js_results"
        app.session_state["lang"] = "en"
        app.session_state["skills"] = ["excel", "crm administration"]
        app.run()
        self.assertEqual(list(app.exception), [])
        title = T("en")["sdg_open_btn"]
        self.assertEqual(app.button(key="sdg_toggle_btn").label, "▸ " + title)
        app.button(key="sdg_toggle_btn").click().run()
        self.assertTrue(app.session_state["show_sdg_wheel"])
        self.assertEqual(app.button(key="sdg_toggle_btn").label, "▾ " + title)
        self.assertEqual(list(app.exception), [])
        app.button(key="sdg_toggle_btn").click().run()
        self.assertFalse(app.session_state["show_sdg_wheel"])
        self.assertEqual(app.button(key="sdg_toggle_btn").label, "▸ " + title)
        self.assertEqual(list(app.exception), [])
