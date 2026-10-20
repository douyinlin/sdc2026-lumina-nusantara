"""Manual check: does the CV intake detect skills from a synthetic CV?

Run:  python tests/check_cv_intake.py
This is a plain script (not a unittest) so it can import Streamlit widgets.
"""

import io
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# --------------------------------------------------------------------------- #
# Minimal Streamlit stub so app.py can be imported without a server.
# --------------------------------------------------------------------------- #
import streamlit  # noqa: E402  (real package must exist for the exec below)


def _noop(*args, **kwargs):
    return None


class _Sidebar:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


for name in (
    "set_page_config", "title", "caption", "header", "subheader", "divider",
    "success", "warning", "info", "write", "markdown", "dataframe", "metric",
    "table", "selectbox", "multiselect", "radio", "file_uploader", "stop",
):
    setattr(streamlit, name, _noop)
streamlit.sidebar = _Sidebar()
streamlit.expander = lambda *a, **k: _Sidebar()
streamlit.columns = lambda *a, **k: [_Sidebar() for _ in range(8)]

# --------------------------------------------------------------------------- #
# Load helpers directly from app.py source (skip the UI section).
# --------------------------------------------------------------------------- #
src = (ROOT / "app.py").read_text(encoding="utf-8")
start = src.index("SKILL_OPTIONS = sorted(")
end = src.index("# UI")
from utils import Role  # noqa: E402
from datetime import date  # noqa: E402

namespace: dict = {"Role": Role, "date": date}
exec(compile(src[start:end], "app_helpers", "exec"), namespace)

extract = namespace["extract_profile_from_upload"]


class FakeUpload:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._buffer = io.BytesIO(data)

    def read(self) -> bytes:
        return self._buffer.read()


CV_TEXT = """Nur Aisyah binti Rahman - Customer Service Team Lead
Kuala Lumpur, Malaysia

EXPERIENCE
2019-2025  Team Lead, Customer Support, Telekom SME Desk
  - Managed a team of 8 agents handling Zendesk tickets
  - Built monthly reporting dashboards in Excel and Power BI
  - Ran chatgpt prompt library to cut response drafting time by 30%

SKILLS
Customer support, Excel, Power BI dashboard, Zendesk, basic SQL, Python (pandas)
"""

DETECTED = extract(FakeUpload("synthetic_cv.txt", CV_TEXT.encode()))

EXPECTED = {
    "customer support", "excel", "data visualisation", "crm administration",
    "prompt engineering", "team lead", "sql", "python", "reporting",
}

print("Detected:", sorted(DETECTED))
missing = EXPECTED - set(DETECTED)
print("Missing :", sorted(missing) or "none")
print("Extra   :", sorted(set(DETECTED) - EXPECTED) or "none")
print("RESULT  :", "PASS" if not missing else "FAIL")
sys.exit(0 if not missing else 1)
