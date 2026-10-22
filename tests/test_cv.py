import io
import unittest
from src.cv import cv_to_skills

class TestCV(unittest.TestCase):
    def test_synthetic_text(self):
        upload = io.BytesIO(b"Fictional demo profile: SQL, Python, Excel. SQL.")
        upload.name = "fictional.txt"
        skills = cv_to_skills(upload)
        self.assertTrue({"sql", "python", "excel"}.issubset(skills))
        self.assertEqual(len(skills), len(set(skills)))

    def test_empty_and_unsupported_pdf(self):
        for name, raw in [("empty.txt", b""), ("scan.pdf", b"%PDF-no extractable text")]:
            upload = io.BytesIO(raw)
            upload.name = name
            self.assertEqual(cv_to_skills(upload), [])
