"""Presentation regressions: model values are displayed, never re-scored."""
import unittest
from src.presentation import CSS_PATH, copy_for, flow_header, learning_path, score_panel, skill_chips


class PresentationTests(unittest.TestCase):
    def test_score_is_not_rescaled_or_treated_as_probability(self):
        html = score_panel(58.5, [("Coverage", .84), ("Gap cost", .45)], "en")
        self.assertIn("58.5", html)
        self.assertIn("/ 100", html)
        self.assertIn("84%", html)
        self.assertIn("45%", html)
        self.assertIn("--meter-width:84.00%", html)

    def test_zero_and_full_values(self):
        html = score_panel(0, [("Zero", 0), ("Full", 1)], "en")
        self.assertIn("--meter-width:0.00%", html)
        self.assertIn("--meter-width:100.00%", html)

    def test_dynamic_content_is_escaped(self):
        self.assertNotIn("<script>", skill_chips(["<script>"]))
        self.assertIn("&lt;script&gt;", skill_chips(["<script>"]))
        self.assertIn("&lt;flow&gt;", flow_header("js_intake", "<flow>", "en"))
        self.assertIn("&quot;", score_panel(10, [('a"b', .2)], "en"))

    def test_path_preserves_engine_steps_and_durations(self):
        html = learning_path([(3, "SQL & reporting", 7), (8, "Python", 2)], "en")
        self.assertLess(html.index(">03<"), html.index(">08<"))
        self.assertIn("7 weeks", html)
        self.assertIn("2 weeks", html)
        self.assertIn("SQL &amp; reporting", html)

    def test_each_locale_has_all_ui_strings(self):
        for lang in ("zh", "ms"):
            self.assertEqual(set(copy_for("en")), set(copy_for(lang)))
        self.assertEqual(copy_for("unknown"), copy_for("en"))

    def test_current_step_and_reduced_motion(self):
        for flow in ("js", "hr", "cc"):
            html = flow_header(flow + "_results", "Flow", "zh")
            self.assertEqual(html.count('aria-current="step"'), 1)
            self.assertIn("探索分析结果", html)
        self.assertIn("prefers-reduced-motion: reduce", CSS_PATH.read_text())


if __name__ == "__main__":
    unittest.main()
