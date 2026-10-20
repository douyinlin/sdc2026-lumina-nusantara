"""SkillRadar MY — Streamlit application.

One-click start:  python app.py   (installs Streamlit automatically if missing)
Streamlit way   :  streamlit run app.py

The matching / pathway / SDG engine lives in ``src/utils.py``; this file only
handles screens and rendering so the engine stays unit-testable.

The ``try`` block below is deliberate: on a fresh Replit (or any fresh machine)
``streamlit`` may not be installed yet. Instead of crashing with
ModuleNotFoundError we install the dependency and hand off to Streamlit.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent


def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:  # pragma: no cover
        return False


def _bootstrap() -> None:
    """Install Streamlit if missing, then relaunch this file under Streamlit."""
    try:
        import streamlit  # noqa: F401
    except ModuleNotFoundError:
        print("[SkillRadar] Installing Streamlit (one time) ...", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "streamlit", "pandas"])
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(Path(__file__).resolve()),
            "--server.port",
            os.environ.get("PORT", "8501"),
            "--server.address",
            "0.0.0.0",
            "--server.headless",
            "true",
        ],
    )


if not _running_under_streamlit():
    _bootstrap()

import streamlit as st  # noqa: E402

sys.path.insert(0, str(ROOT / "src"))

from utils import Role, pathway, rank, sdg_summary  # noqa: E402

TREND_FILE = ROOT / "data" / "trends" / "latest.json"

# --------------------------------------------------------------------------- #
# Seed data — synthetic demo profile and a curated role catalogue.
# Domain 1 rule: public / synthetic data only, never real CVs.
# --------------------------------------------------------------------------- #

SKILL_OPTIONS = sorted(
    {
        "customer support",
        "excel",
        "sql",
        "python",
        "data visualisation",
        "prompt engineering",
        "crm administration",
        "project management",
        "product management",
        "machine learning",
        "team lead",
        "reporting",
    }
)

ROLE_CATALOGUE = [
    Role("AI Operations Specialist", ["prompt engineering", "data visualisation", "sql", "customer support"], 0.8, ["4.4", "8.5"]),
    Role("Customer Success Analyst", ["crm administration", "data visualisation", "sql"], 0.2, ["8.5", "4.4"]),
    Role("Data Steward", ["sql", "excel", "data visualisation"], 0.1, ["9.1", "8.5"]),
    Role("Machine Learning Engineer", ["python", "machine learning", "sql"], 0.9, ["9.1", "4.4"]),
    Role("Product Manager (AI)", ["product management", "project management", "prompt engineering"], 0.6, ["8.2", "4.4"]),
    Role("Process Automation Lead", ["excel", "python", "project management", "prompt engineering"], 0.5, ["8.2", "9.1"]),
    Role("Data Entry Specialist", ["excel", "reporting"], -0.9, ["8.5"]),
]

DEMO_PROFILES = {
    "Customer-service supervisor (synthetic)": ["customer support", "excel", "team lead"],
    "Fresh graduate (synthetic)": ["python", "reporting"],
    "HR manager (synthetic)": ["project management", "excel", "crm administration"],
}

DEFAULT_TREND = {
    "source_url": "https://www.weforum.org/publications/the-future-of-jobs-report-2025/",
    "retrieved_at": date(2026, 10, 20).isoformat(),
    "note": "Bundled seed snapshot. Replace data/trends/latest.json with a freshly "
    "fetched snapshot before the demo and the dates below will update.",
    "signals": [
        {"skill": "prompt engineering", "direction": "rising", "weight": 0.4},
        {"skill": "data visualisation", "direction": "rising", "weight": 0.2},
        {"skill": "sql", "direction": "stable", "weight": 0.1},
        {"skill": "customer support", "direction": "declining", "weight": -0.3},
        {"skill": "excel", "direction": "stable", "weight": 0.0},
        {"skill": "machine learning", "direction": "rising", "weight": 0.5},
    ],
}


def load_trend() -> dict:
    if TREND_FILE.exists():
        try:
            return json.loads(TREND_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return DEFAULT_TREND


def scenario_weight(trend: dict) -> dict[str, float]:
    """Map trend signals onto role names by skill overlap."""
    weights: dict[str, float] = {}
    for role in ROLE_CATALOGUE:
        relevant = [s for s in trend.get("signals", []) if s["skill"] in role.required_skills]
        delta = sum(s["weight"] for s in relevant) / max(len(relevant), 1)
        weights[role.name] = max(-1.0, min(1.0, role.trend + delta))
    return weights


def apply_trend(trend: dict) -> list[Role]:
    weights = scenario_weight(trend)
    return [Role(r.name, r.required_skills, weights[r.name], r.sdg) for r in ROLE_CATALOGUE]


# --------------------------------------------------------------------------- #
# CV intake — "Skills profile intake" (Domain 1 must-have feature #1)
# --------------------------------------------------------------------------- #

SKILL_ALIASES = {
    "customer service": "customer support",
    "client service": "customer support",
    "helpdesk": "customer support",
    "spreadsheet": "excel",
    "excel": "excel",
    "structured query language": "sql",
    "sql": "sql",
    "power bi": "data visualisation",
    "tableau": "data visualisation",
    "dashboard": "data visualisation",
    "chatgpt": "prompt engineering",
    "genai": "prompt engineering",
    "generative ai": "prompt engineering",
    "llm": "prompt engineering",
    "salesforce": "crm administration",
    "zendesk": "crm administration",
    "hubspot": "crm administration",
    "crm": "crm administration",
    "pmp": "project management",
    "agile": "project management",
    "scrum": "project management",
    "roadmap": "product management",
    "stakeholder": "product management",
    "python": "python",
    "pandas": "python",
    "machine learning": "machine learning",
    "pytorch": "machine learning",
    "tensorflow": "machine learning",
    "supervisor": "team lead",
    "team lead": "team lead",
    "manager": "team lead",
    "reporting": "reporting",
}


def _read_uploaded_text(uploaded) -> str:
    """Return plain text from a .txt/.md upload or a text-based .pdf upload."""
    raw = uploaded.read()
    name = (getattr(uploaded, "name", "") or "").lower()

    if name.endswith(".pdf"):
        # Minimal PDF text extraction: pull text out of Flate-compressed streams.
        import re
        import zlib

        chunks: list[str] = []
        for match in re.finditer(rb"stream\r?\n", raw):
            start = match.end()
            end = raw.find(b"endstream", start)
            if end == -1:
                continue
            try:
                blob = zlib.decompress(raw[start:end])
            except Exception:
                continue
            for literal in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)\s*Tj", blob):
                chunks.append(literal.group(1).decode("latin-1", "ignore"))
            for array in re.finditer(rb"\[(.*?)\]\s*TJ", blob, re.S):
                for literal in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)", array.group(1)):
                    chunks.append(literal.group(1).decode("latin-1", "ignore"))
        return " ".join(chunks)

    return raw.decode("utf-8", "ignore")


def extract_profile_from_upload(uploaded) -> list[str]:
    """Map uploaded CV text onto the controlled skill vocabulary."""
    text = _read_uploaded_text(uploaded).lower()
    if not text.strip():
        return []

    found: list[str] = []
    for alias, skill in SKILL_ALIASES.items():
        if alias in text and skill not in found:
            found.append(skill)

    # Keep only skills the app actually knows about.
    return [s for s in found if s in SKILL_OPTIONS]


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="SkillRadar MY", page_icon="📡", layout="wide")

st.title("📡 SkillRadar MY")
st.caption(
    "Lumina Nusantara · SDC 2026 · Domain 1 — every forecast carries its source and "
    "retrieval date; every role maps to the SDGs."
)

trend = load_trend()
roles = apply_trend(trend)

with st.sidebar:
    st.header("1 · Who are you today?")

    # ---- Two intake paths required by Domain 1: CV upload OR questionnaire ----
    intake_mode = st.radio(
        "How would you like to tell us about yourself?",
        options=["Upload a CV (PDF / TXT)", "Fill a short questionnaire"],
        help="Domain 1 rule: use synthetic documents only — never upload a real CV.",
    )

    detected_from_cv: list[str] = []

    if intake_mode.startswith("Upload"):
        uploaded = st.file_uploader(
            "Drop a CV here (synthetic only)",
            type=["txt", "pdf", "md"],
            help="PDF text is extracted automatically. Nothing is stored or sent anywhere.",
        )
        if uploaded is not None:
            detected_from_cv = extract_profile_from_upload(uploaded)
            if detected_from_cv:
                st.success(f"Detected {len(detected_from_cv)} skill(s): {', '.join(detected_from_cv)}")
            else:
                st.warning(
                    "No known skill was detected. Try the questionnaire, or add the skill names "
                    "to the CV text (we match against a fixed skill vocabulary)."
                )
        st.caption("No CV handy? Use one of the sample profiles below.")

    demo_choice = st.selectbox("Start from a profile", ["Custom"] + list(DEMO_PROFILES))
    if demo_choice == "Custom":
        default_skills = detected_from_cv or ["customer support", "excel"]
    else:
        default_skills = DEMO_PROFILES[demo_choice]

    profile = st.multiselect("Your current skills (editable)", SKILL_OPTIONS, default=default_skills)

    st.header("2 · Scenario")
    scenario = st.radio(
        "AI disruption speed",
        options=["moderate", "fast"],
        format_func=lambda x: "Moderate disruption" if x == "moderate" else "Fast disruption",
    )
    st.caption("Predictions are estimates, not facts. We show both scenarios.")

    st.divider()
    st.header("Trend data")
    st.caption(f"**Source:** {trend['source_url']}")
    st.caption(f"**Retrieved:** {trend['retrieved_at']}")
    if trend.get("note"):
        st.info(trend["note"])

if not profile:
    st.warning("Pick at least one skill in the sidebar to start.")
    st.stop()

results = rank(profile, roles, scenario=scenario)
top = results[0]

col_a, col_b = st.columns((2, 1))

with col_a:
    st.subheader("Future Skills Radar")
    rows = [
        {
            "Skill": s["skill"],
            "Direction": s["direction"],
            "Weight": s["weight"],
            "Source": trend["source_url"],
            "Retrieved": trend["retrieved_at"],
        }
        for s in trend.get("signals", [])
        if s["skill"] in profile or s["direction"] == "rising"
    ]
    st.dataframe(rows, width="stretch", hide_index=True)

with col_b:
    st.subheader("SDG contribution")
    summary = sdg_summary(results[:4])
    st.metric("SDG tags in your shortlist", sum(summary.values()))
    st.write(
        "\n".join(f"- **{k}** — {v} role(s)" for k, v in summary.items())
        or "No tags yet."
    )

st.divider()
st.subheader("Ranked future roles")
st.caption(f"Scenario: **{scenario}** · match score is out of 100 and fully decomposed below.")

for r in results[:4]:
    c = r["components"]
    with st.expander(f"{r['score']:.1f}  ·  {r['role']}  ·  SDG {', '.join(r['sdg'])}"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Skill coverage", f"{c['coverage'] * 100:.0f}%")
        m2.metric("Transferability", f"{c['transfer'] * 100:.0f}%")
        m3.metric("Demand trend", f"{c['trend'] * 100:.0f}%")
        m4.metric("Gap cost", f"{c['gap_cost'] * 100:.0f}%")
        st.write(f"**You already have:** {', '.join(r['covered']) or '—'}")
        st.write(f"**Skills to close:** {', '.join(r['missing']) or 'none'}")

st.divider()
st.subheader("Your reskilling pathway")
st.caption(f"First step towards **{top['role']}** — ordered cheapest-first, all resources free or HRD Corp-claimable.")

if top["missing"]:
    st.table(pathway(top))
else:
    st.success("You already cover every skill for this role. Consider the next role in the ranking.")

st.divider()
with st.expander("Comparison across scenarios (this is how uncertainty is handled)"):
    moderate = rank(profile, roles, scenario="moderate")
    fast = rank(profile, roles, scenario="fast")
    st.dataframe(
        [
            {
                "Role": m["role"],
                "Moderate score": m["score"],
                "Fast score": f["score"],
                "Δ": round(f["score"] - m["score"], 1),
            }
            for m, f in zip(moderate, fast)
        ],
        width="stretch",
        hide_index=True,
    )

st.caption(
    f"Data: {trend['source_url']} (retrieved {trend['retrieved_at']}). "
    "This tool supports human career decisions; it does not replace them."
)
