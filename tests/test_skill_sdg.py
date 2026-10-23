"""Every catalogue skill must map to at least one SDG target."""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


class TestSkillSdg(unittest.TestCase):
    def setUp(self):
        self.roles = json.loads((DATA / "roles.json").read_text(encoding="utf-8"))["roles"]
        self.map = json.loads((DATA / "skills_sdg.json").read_text(encoding="utf-8"))["skills"]

    def test_every_catalogue_skill_is_mapped(self):
        skills = sorted({s["skill"] for r in self.roles for s in r["skills"]})
        missing = [s for s in skills if s not in self.map]
        self.assertEqual(missing, [], f"skills without an SDG target: {missing}")

    def test_targets_look_like_sdg_targets(self):
        for skill, info in self.map.items():
            with self.subTest(skill=skill):
                self.assertTrue(info["targets"], "no target listed")
                for target in info["targets"]:
                    self.assertRegex(target, r"^\d{1,2}\.(\d{1,2}|[a-z])$")
                    self.assertTrue(1 <= int(target.split(".")[0]) <= 17)

    def test_skill_sdg_file_says_it_is_not_official(self):
        note = json.loads((DATA / "skills_sdg.json").read_text(encoding="utf-8"))["note"].lower()
        self.assertIn("not an official", note)


if __name__ == "__main__":
    unittest.main()
