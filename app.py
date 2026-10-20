"""SkillRadar MY — guided application.

Flow:  landing (choose who you are)  ->  intake (full screen)  ->  results
       * Jobseeker: CV upload or categorised questionnaire -> matches, gap, pathway, SDG
       * HR: team roster -> workforce gap heatmap, priority gaps, reskilling plan

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
import re
import sys
import zlib
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from utils import Role, pathway, rank, sdg_summary  # noqa: E402
from i18n import STRINGS, T, cat  # noqa: E402

DATA = ROOT / "data"
TREND_FILE = DATA / "trends" / "latest.json"

# --------------------------------------------------------------------------- #
# Skill taxonomy — every skill maps to an engine key so scoring stays simple.
# --------------------------------------------------------------------------- #

TAXONOMY: dict[str, dict[str, list[str]]] = {
    "📊 Office & Data": {
        "Excel / spreadsheets": ["excel"],
        "SQL & databases": ["sql"],
        "Data visualisation (Power BI, Tableau)": ["data visualisation"],
        "Reporting & dashboards": ["reporting"],
        "Basic statistics": ["basic statistics"],
        "Data entry & cleaning": ["data entry"],
        "Research & analysis": ["research"],
    },
    "💻 Tech & AI": {
        "Python programming": ["python"],
        "Web development (HTML/CSS/JS)": ["web development"],
        "Machine learning": ["machine learning"],
        "Generative AI / prompt engineering": ["prompt engineering"],
        "Cloud platforms (AWS, GCP, Azure)": ["cloud"],
        "Process automation (RPA, scripts)": ["automation"],
        "IT support & troubleshooting": ["it support"],
        "Cybersecurity basics": ["cybersecurity"],
    },
    "🎧 Customer & Operations": {
        "Customer support": ["customer support"],
        "CRM tools (Salesforce, Zendesk)": ["crm administration"],
        "Operations & process improvement": ["process improvement"],
        "Supply chain & procurement": ["supply chain"],
        "Quality assurance": ["quality assurance"],
        "Inventory & warehouse management": ["inventory"],
    },
    "👥 People & Management": {
        "Team leadership": ["team lead"],
        "Project management": ["project management"],
        "Product management": ["product management"],
        "Recruitment & talent acquisition": ["recruitment"],
        "HR operations & payroll": ["hr operations"],
        "Coaching & mentoring": ["coaching"],
    },
    "🗣 Communication & Language": {
        "Business communication": ["communication"],
        "Stakeholder management": ["stakeholder management"],
        "Presentation & public speaking": ["presentation"],
        "Negotiation": ["negotiation"],
        "English (professional)": ["english"],
        "Bahasa Malaysia": ["bahasa"],
        "Mandarin / Chinese": ["mandarin"],
    },
    "💰 Finance & Accounting": {
        "Bookkeeping & double entry": ["bookkeeping"],
        "Financial reporting (MFRS/IFRS)": ["financial reporting"],
        "Budgeting & forecasting": ["budgeting"],
        "Tax compliance": ["tax"],
        "Audit support": ["audit"],
        "Financial modelling": ["financial modelling"],
    },
    "📣 Sales & Marketing": {
        "B2B sales & pipeline management": ["sales"],
        "Digital marketing (SEO, ads)": ["digital marketing"],
        "Social media & content": ["content"],
        "Brand & copywriting": ["copywriting"],
        "Market research": ["market research"],
        "Customer segmentation": ["segmentation"],
    },
    "🎨 Design & Creative": {
        "Graphic design (Figma, Canva)": ["graphic design"],
        "UI / UX design": ["ui ux"],
        "Video editing": ["video editing"],
        "Photography": ["photography"],
    },
    "🏭 Manufacturing & Logistics": {
        "Lean / Six Sigma": ["lean"],
        "Machine operation & maintenance": ["machine operation"],
        "Health & safety (OSH)": ["osh"],
        "Logistics coordination": ["logistics"],
        "Forklift / heavy equipment": ["heavy equipment"],
    },
    "🏥 Health, Care & Education": {
        "Patient care": ["patient care"],
        "Clinic / hospital administration": ["clinic admin"],
        "Teaching & curriculum design": ["teaching"],
        "Counselling & support": ["counselling"],
        "First aid & CPR": ["first aid"],
    },
    "⚖️ Legal, Compliance & Admin": {
        "Contract review": ["contract review"],
        "Regulatory compliance": ["compliance"],
        "Company secretarial work": ["company secretary"],
        "Office administration": ["office admin"],
        "Documentation & records": ["documentation"],
    },
}

LABEL_TO_KEYS = {label: keys for group in TAXONOMY.values() for label, keys in group.items()}

ALIASES = {
    "customer service": "customer support", "helpdesk": "customer support",
    "zendesk": "crm administration", "salesforce": "crm administration",
    "crm": "crm administration", "power bi": "data visualisation",
    "tableau": "data visualisation", "dashboard": "data visualisation",
    "chatgpt": "prompt engineering", "genai": "prompt engineering",
    "generative ai": "prompt engineering", "llm": "prompt engineering",
    "spreadsheet": "excel", "pandas": "python", "pytorch": "machine learning",
    "tensorflow": "machine learning", "agile": "project management",
    "scrum": "project management", "pmp": "project management",
    "supervisor": "team lead", "manager": "team lead",
    "stakeholder": "stakeholder management", "presentation": "presentation",
    "rpa": "automation", "automation": "automation",
    "process improvement": "process improvement",
    "communication": "communication",
}

DEFAULT_ROLES = [
    Role("AI Operations Specialist", ["prompt engineering", "data visualisation", "sql", "customer support"], 0.8, ["4.4", "8.5"]),
    Role("Customer Success Analyst", ["crm administration", "data visualisation", "sql"], 0.2, ["8.5", "4.4"]),
    Role("Data Steward", ["sql", "excel", "data visualisation"], 0.1, ["9.1", "8.5"]),
    Role("Machine Learning Engineer", ["python", "machine learning", "sql"], 0.9, ["9.1", "4.4"]),
    Role("Product Manager (AI)", ["product management", "project management", "prompt engineering"], 0.6, ["8.2", "4.4"]),
    Role("Process Automation Lead", ["excel", "python", "project management", "prompt engineering"], 0.5, ["8.2", "9.1"]),
]


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #

def load_roles() -> list[Role]:
    path = DATA / "experimental.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [Role(**r) for r in raw["roles"]]
    except Exception:
        return DEFAULT_ROLES


def load_trend() -> dict:
    try:
        return json.loads(TREND_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"is_simulated": True, "source_url": None, "retrieved_at": None,
                "note": "Simulated weights for demonstration.", "signals": []}


def apply_trend(roles: list[Role], trend: dict) -> list[Role]:
    signals = trend.get("signals") or []
    out = []
    for role in roles:
        relevant = [s["weight"] for s in signals if s["skill"] in role.required_skills]
        delta = sum(relevant) / len(relevant) if relevant else 0.0
        out.append(Role(role.name, role.required_skills, max(-1.0, min(1.0, role.trend + delta)), role.sdg))
    return out


def cv_to_skills(uploaded) -> list[str]:
    raw = uploaded.read()
    name = (getattr(uploaded, "name", "") or "").lower()
    if name.endswith(".pdf"):
        chunks = []
        for m in re.finditer(rb"stream\r?\n", raw):
            start, end = m.end(), raw.find(b"endstream", m.end())
            if end == -1:
                continue
            try:
                blob = zlib.decompress(raw[start:end])
            except Exception:
                continue
            chunks += [t.group(1).decode("latin-1", "ignore")
                       for t in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)\s*Tj", blob)]
            for arr in re.finditer(rb"\[(.*?)\]\s*TJ", blob, re.S):
                chunks += [t.group(1).decode("latin-1", "ignore")
                           for t in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)", arr.group(1))]
        text = " ".join(chunks)
    else:
        text = raw.decode("utf-8", "ignore")
    low = text.lower()
    found: list[str] = []
    for alias, key in ALIASES.items():
        if alias in low and key not in found:
            found.append(key)
    return found


# --------------------------------------------------------------------------- #
# Motion — 1s intro curtain on load, and a 0.7s transition on stage changes.
# Pure CSS: no rerun, no server work, works on Streamlit Cloud.
# --------------------------------------------------------------------------- #

ANIM_CSS = """
<style>
@keyframes sr-curtain {
  0%   { opacity: 1; }
  84%  { opacity: 1; }
  100% { opacity: 0; visibility: hidden; }
}
@keyframes sr-eyebrow {
  0%   { opacity: 0; transform: translateY(6px); letter-spacing: .05em; }
  100% { opacity: 1; transform: translateY(0); letter-spacing: .22em; }
}
@keyframes sr-mark {
  0%   { opacity: 0; transform: scale(.94); letter-spacing: -1.5px; }
  45%  { opacity: 1; letter-spacing: .5px; }
  100% { opacity: 1; transform: scale(1); letter-spacing: -.5px; }
}
@keyframes sr-tagline {
  0%   { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes sr-brand {
  0%   { opacity: 0; transform: translateY(8px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes sr-sweep {
  0%   { transform: translateX(-120%); }
  100% { transform: translateX(120%); }
}
@keyframes sr-rise {
  0%   { opacity: 0; transform: translateY(14px); }
  100% { opacity: 1; transform: translateY(0); }
}
.sr-curtain {
  position: fixed; inset: 0; z-index: 999999; text-align: center;
  display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 50% 40%, #fbfdf7 0%, #eff4e8 46%, #dfe8d3 100%);
  animation: sr-curtain 2.2s ease forwards;
  pointer-events: none;
}
.sr-curtain-inner { max-width: 860px; padding: 0 28px; }
.sr-eyebrow {
  font-size: 12px; font-weight: 600; color: #7a8663; text-transform: uppercase;
  letter-spacing: .22em; margin-bottom: 16px;
  animation: sr-eyebrow .7s ease-out both;
}
.sr-mark {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 42px; font-weight: 800; color: #4b5a2a; line-height: 1.15;
  animation: sr-mark 1s cubic-bezier(.2,.8,.25,1) .12s both;
}
.sr-tagline {
  margin-top: 14px; color: #62704f; font-size: 14.5px; line-height: 1.7;
  animation: sr-tagline .9s ease-out .55s both;
}
.sr-brand {
  margin-top: 22px; font-size: 13px; font-weight: 650; color: #8A9A5B;
  letter-spacing: .16em; text-transform: uppercase;
  animation: sr-brand .8s ease-out 1s both;
}
.sr-bar {
  position: absolute; bottom: 0; left: 0; height: 3px; width: 100%;
  background: linear-gradient(90deg, transparent, #8A9A5B, #5b7fa6, #8A9A5B, transparent);
  animation: sr-sweep 2.2s ease forwards;
}
.sr-enter { animation: sr-rise 0.55s ease-out both; }
</style>
"""

INTRO_HTML = """
<div class="sr-curtain">
  <div class="sr-curtain-inner">
    <div class="sr-eyebrow">SDC 2026 · Domain 1 · SDG 4</div>
    <div class="sr-mark">The Future-Ready Workforce</div>
    <div class="sr-tagline">
      Tracking AI's advance · forecasting rising and declining skills ·
      matching people to future roles · personalised reskilling ·
      every role mapped to the UN SDGs
    </div>
    <div class="sr-brand">📡 SkillRadar MY</div>
  </div>
  <div class="sr-bar"></div>
</div>
"""

# --------------------------------------------------------------------------- #
# Landing look — animated gradient sky, floating orbs, glass cards.
# --------------------------------------------------------------------------- #

LANDING_CSS = """
<style>
@keyframes sr-float-a { 0%{transform:translate3d(0,0,0) scale(1)} 50%{transform:translate3d(30px,-38px,0) scale(1.08)} 100%{transform:translate3d(0,0,0) scale(1)} }
@keyframes sr-float-b { 0%{transform:translate3d(0,0,0) scale(1)} 50%{transform:translate3d(-42px,26px,0) scale(1.12)} 100%{transform:translate3d(0,0,0) scale(1)} }
@keyframes sr-float-c { 0%{transform:translate3d(0,0,0) scale(1)} 50%{transform:translate3d(24px,34px,0) scale(0.92)} 100%{transform:translate3d(0,0,0) scale(1)} }
@keyframes sr-sky     { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes sr-glow    { 0%,100%{opacity:.45} 50%{opacity:.95} }

[data-testid="stAppViewContainer"] {
  background: linear-gradient(135deg, #f6faf0 0%, #eaf1dd 28%, #e6eef6 62%, #f7f3ea 100%);
  background-size: 220% 220%;
  animation: sr-sky 22s ease-in-out infinite;
}
[data-testid="stHeader"] { background: transparent; }

.sr-orb { position: fixed; border-radius: 50%; filter: blur(52px); pointer-events: none; z-index: 0; opacity:.75; }
.sr-o1 { width: 340px; height: 340px; top: -70px; left: -60px;
         background: radial-gradient(circle, rgba(138,154,91,.50), rgba(138,154,91,0) 70%);
         animation: sr-float-a 16s ease-in-out infinite; }
.sr-o2 { width: 300px; height: 300px; top: 12%; right: -80px;
         background: radial-gradient(circle, rgba(91,127,166,.42), rgba(91,127,166,0) 70%);
         animation: sr-float-b 19s ease-in-out infinite; }
.sr-o3 { width: 260px; height: 260px; bottom: 4%; left: 18%;
         background: radial-gradient(circle, rgba(192,138,75,.35), rgba(192,138,75,0) 70%);
         animation: sr-float-c 21s ease-in-out infinite; }
.sr-o4 { width: 220px; height: 220px; bottom: 24%; right: 20%;
         background: radial-gradient(circle, rgba(120,170,140,.32), rgba(120,170,140,0) 70%);
         animation: sr-float-a 26s ease-in-out infinite reverse; }

.sr-hero { text-align: center; position: relative; z-index: 2; padding: 22px 0 4px; }
.sr-badge { display: inline-block; padding: 5px 14px; border-radius: 999px; font-size: 11.5px;
            letter-spacing: .12em; text-transform: uppercase; color: #5d6b36;
            background: rgba(138,154,91,.14); border: 1px solid rgba(138,154,91,.35); }
.sr-h1 { font-size: 50px; font-weight: 800; margin: 12px 0 4px; letter-spacing: -1.5px;
         background: linear-gradient(92deg, #4b5a2a 0%, #7b8f4a 45%, #4e6b8a 100%);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sr-sub { color: #5f6b52; font-size: 15.5px; max-width: 720px; margin: 0 auto; line-height: 1.6; }

[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.78) !important;
  border: 1px solid rgba(255,255,255,.9) !important;
  border-radius: 22px !important;
  box-shadow: 0 18px 46px rgba(76,86,52,.14);
  transition: transform .28s ease, box-shadow .28s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-6px);
  box-shadow: 0 26px 62px rgba(76,86,52,.22);
}
.sr-icon { font-size: 40px; line-height: 1; }
.sr-title { font-size: 24px; font-weight: 750; color: #38401f; margin: 6px 0 4px; }
.sr-desc { color: #5f6b52; font-size: 14px; line-height: 1.55; margin-bottom: 8px; }
.sr-list { list-style: none; padding: 0; margin: 0 0 12px; }
.sr-list li { color: #55603f; font-size: 13px; line-height: 1.7; }

.stButton > button {
  border-radius: 999px !important; font-weight: 650 !important;
  padding: .62rem 1rem !important; transition: transform .2s ease, box-shadow .2s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(76,86,52,.22); }
.stButton > button[kind="primary"] {
  background: linear-gradient(96deg, #8A9A5B 0%, #6f8140 55%, #5b7fa6 130%) !important;
  border: none !important; color: #fff !important; letter-spacing: .02em;
  box-shadow: 0 10px 26px rgba(111,129,64,.32);
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.06); }

.sr-steps { display:flex; gap:14px; justify-content:center; margin: 20px auto 0; max-width: 900px; }
.sr-step { flex:1; background: rgba(255,255,255,.55); border:1px solid rgba(255,255,255,.85);
           border-radius:16px; padding:12px 14px; text-align:center; }
.sr-step b { display:block; color:#3f4a26; font-size:13.5px; margin-bottom:3px; }
.sr-step span { color:#6b7560; font-size:12px; line-height:1.5; }
.sr-step em { font-style:normal; font-size:17px; }

.sr-foot { text-align: center; color: #7a836a; font-size: 12.5px; margin-top: 16px; }
.sr-pulse { display:inline-block; width:8px; height:8px; border-radius:50%;
            background:#8A9A5B; margin-right:7px; animation: sr-glow 1.8s ease-in-out infinite; }
</style>
"""

ORBS_HTML = """
<div class="sr-orb sr-o1"></div>
<div class="sr-orb sr-o2"></div>
<div class="sr-orb sr-o3"></div>
<div class="sr-orb sr-o4"></div>
"""

# Shared look for every screen after the landing: same palette, calmer motion.
APP_CSS = """
<style>
@keyframes sr-sky { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes sr-rise { 0%{opacity:0; transform:translateY(12px)} 100%{opacity:1; transform:translateY(0)} }
@keyframes sr-glow { 0%,100%{opacity:.45} 50%{opacity:.95} }

[data-testid="stAppViewContainer"] {
  background: linear-gradient(135deg, #f7faf2 0%, #eef3e6 34%, #eaf0f6 68%, #f8f4ec 100%);
  background-size: 200% 200%;
  animation: sr-sky 26s ease-in-out infinite;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(255,255,255,.72); }

h1, h2, h3, h4 { color: #3f4a26 !important; letter-spacing: -.01em; }
h3 { border-left: 4px solid #8A9A5B; padding-left: 10px; }
p, li, label, .stMarkdown { color: #4c5540; }

/* glass panels */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.78) !important;
  border: 1px solid rgba(255,255,255,.9) !important;
  border-radius: 20px !important;
  box-shadow: 0 14px 34px rgba(76,86,52,.12);
  transition: transform .25s ease, box-shadow .25s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 44px rgba(76,86,52,.18);
}

/* buttons */
.stButton > button, .stDownloadButton > button {
  border-radius: 999px !important; font-weight: 640 !important;
  transition: transform .2s ease, box-shadow .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px); box-shadow: 0 10px 22px rgba(76,86,52,.20);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(96deg, #8A9A5B 0%, #6f8140 55%, #5b7fa6 130%) !important;
  border: none !important; color: #fff !important;
  box-shadow: 0 10px 26px rgba(111,129,64,.30);
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.06); }
.stButton > button:not([kind="primary"]) {
  background: rgba(255,255,255,.75) !important;
  border: 1px solid rgba(138,154,91,.45) !important;
  color: #4b5a2a !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid rgba(138,154,91,.25); }
.stTabs [data-baseweb="tab"] {
  background: rgba(255,255,255,.6); border-radius: 12px 12px 0 0;
  padding: 8px 16px; color: #55603f;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(180deg, rgba(138,154,91,.22), rgba(138,154,91,.08)) !important;
  color: #3f4a26 !important; font-weight: 650;
}

/* metrics */
[data-testid="stMetric"] {
  background: rgba(255,255,255,.68);
  border: 1px solid rgba(255,255,255,.9);
  border-radius: 16px; padding: 12px 14px;
  box-shadow: 0 8px 22px rgba(76,86,52,.10);
}
[data-testid="stMetricLabel"] { color: #6b7560 !important; }
[data-testid="stMetricValue"] { color: #3f4a26 !important; font-weight: 700 !important; }

/* tables and dataframes */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(138,154,91,.22);
  box-shadow: 0 10px 26px rgba(76,86,52,.08);
}
[data-testid="stDataFrame"] table, [data-testid="stTable"] table { background: rgba(255,255,255,.72); }

/* expanders */
[data-testid="stExpander"] {
  background: rgba(255,255,255,.62);
  border: 1px solid rgba(255,255,255,.9) !important;
  border-radius: 16px !important;
  box-shadow: 0 10px 26px rgba(76,86,52,.08);
  margin-bottom: 8px;
}
[data-testid="stExpander"] summary { font-weight: 620; color: #3f4a26; }

/* inputs */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(255,255,255,.7); border: 1.5px dashed rgba(138,154,91,.55);
  border-radius: 16px;
}
.stMultiSelect [data-baseweb="tag"] {
  background: linear-gradient(96deg, #8A9A5B, #6f8140) !important;
  border-radius: 999px !important;
}
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, #8A9A5B, #5b7fa6) !important;
}
.sr-enter { animation: sr-rise .5s ease-out both; }
.sr-pill { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px;
           color:#5d6b36; background:rgba(138,154,91,.14);
           border:1px solid rgba(138,154,91,.32); margin-bottom:8px; }
</style>
"""


def play_intro() -> None:
    """Show the 1-second curtain once per browser session."""
    if st.session_state.get("intro_done"):
        return
    st.session_state["intro_done"] = True
    st.markdown(ANIM_CSS + INTRO_HTML, unsafe_allow_html=True)


def transition_into(stage: str) -> None:
    """Short curtain + staged reveal, then move to the next screen."""
    st.session_state["stage"] = stage
    st.session_state["entering"] = True
    st.rerun()


SCROLL_JS = """
<script>
(function () {
  const doc = window.parent.document;
  // Streamlit scrolls an inner container, not the window: reset every scroller.
  doc.querySelectorAll('section, div, main').forEach(function (el) {
    if (el.scrollTop && el.scrollTop > 0) { el.scrollTop = 0; }
  });
  window.parent.scrollTo(0, 0);
})();
</script>
"""


def scroll_top() -> None:
    """Jump back to the top so a new step never opens mid-scroll."""
    components.html(SCROLL_JS, height=0, width=0)


def screen_wrap() -> None:
    """Fade content in and reset scroll when arriving from a transition."""
    if st.session_state.pop("entering", False):
        st.markdown(ANIM_CSS, unsafe_allow_html=True)
        st.markdown('<div class="sr-enter">', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        scroll_top()


def go(stage: str) -> None:
    st.session_state["stage"] = stage
    st.session_state["entering"] = True
    st.rerun()


def reset() -> None:
    for k in list(st.session_state):
        if k != "intro_done":
            del st.session_state[k]
    st.session_state["stage"] = "landing"
    st.rerun()


def current_stage() -> str:
    return st.session_state.get("stage") or "landing"


def lang_selector(compact: bool = False) -> None:
    """Language switch — English / 中文."""
    options = ["en", "zh"]
    labels = {"en": "English", "zh": "中文"}
    current = st.session_state.get("lang", "en")
    choice = st.selectbox(
        "" if compact else "Language / 语言",
        options=options,
        index=options.index(current),
        format_func=lambda k: labels[k],
        label_visibility="collapsed" if compact else "visible",
        key=f"lang_{'c' if compact else 'f'}",
    )
    if choice != current:
        st.session_state["lang"] = choice
        st.rerun()


def top_bar(t: dict) -> None:
    left, mid, right, far = st.columns([2, 2, 1, 1])
    with left:
        st.markdown("### 📡 SkillRadar MY")
    with right:
        if st.button(t["reeval"], use_container_width=True, help=t["reeval_help"]):
            reset()
    with far:
        lang_selector(compact=True)


def trend_cards(t: dict, trend: dict) -> None:
    source = trend.get("source_url")
    retrieved = trend.get("retrieved_at")
    label = t["simulated"]
    st.caption(f"**{label}** · {t['source']}: {source or '—'} · {t['retrieved']}: {retrieved or '—'}")
    signals = trend.get("signals") or []
    if not signals:
        st.info("—")
        return
    cols = st.columns(min(3, len(signals)))
    icon = {"rising": "📈", "declining": "📉", "stable": "➖"}
    for i, s in enumerate(signals[:6]):
        with cols[i % len(cols)]:
            st.metric(
                f"{icon.get(s['direction'], '•')} {s['skill']}",
                t.get(s["direction"], s["direction"]),
                t["weight"].format(f"{s['weight']:+.1f}"),
            )


def role_card(t: dict, result: dict, expanded: bool = False) -> None:
    c = result["components"]
    head = f"{result['score']:.1f} · {result['role']} · SDG {', '.join(result['sdg'])}"
    with st.expander(head, expanded=expanded):
        st.progress(min(1.0, result["score"] / 100))
        a, b, c1, d = st.columns(4)
        a.metric(t["coverage"], f"{c['coverage'] * 100:.0f}%")
        b.metric(t["transfer"], f"{c['transfer'] * 100:.0f}%")
        c1.metric(t["trend"], f"{c['trend'] * 100:.0f}%")
        d.metric(t["gapcost"], f"{c['gap_cost'] * 100:.0f}%")
        st.write(f"**{t['have']} ({len(result['covered'])}):** {', '.join(result['covered']) or '—'}")
        st.write(f"**{t['close']} ({len(result['missing'])}):** {', '.join(result['missing']) or t['none']}")
        st.caption(t["estimate"])


# --------------------------------------------------------------------------- #
# Screen: landing
# --------------------------------------------------------------------------- #

def screen_landing() -> None:
    screen_wrap()
    st.markdown(LANDING_CSS + ORBS_HTML, unsafe_allow_html=True)

    _, lang_col = st.columns([5, 1])
    with lang_col:
        lang_selector(compact=True)

    t = T(st.session_state.get("lang", "en"))

    st.markdown(
        f"""
        <div class="sr-hero">
          <div class="sr-badge">{t['eyebrow']}</div>
          <div class="sr-h1">{t['h1']}</div>
          <div class="sr-sub">
            {t['hero_sub']}<br>
            <span style="font-size:13px;color:#7a836a">{t['hero_note']}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="sr-icon">👤</div>
                <div class="sr-title">{t['js_title']}</div>
                <div class="sr-desc">{t['js_desc']}</div>
                <ul class="sr-list">
                  <li>📄 {t['js_b1']}</li>
                  <li>📈 {t['js_b2']}</li>
                  <li>🎯 {t['js_b3']}</li>
                  <li>🛣️ {t['js_b4']}</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t["js_btn"], type="primary", use_container_width=True):
                go("js_intake")
    with right:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="sr-icon">🏢</div>
                <div class="sr-title">{t['hr_title']}</div>
                <div class="sr-desc">{t['hr_desc']}</div>
                <ul class="sr-list">
                  <li>👥 {t['hr_b1']}</li>
                  <li>🔥 {t['hr_b2']}</li>
                  <li>💸 {t['hr_b3']}</li>
                  <li>🌱 {t['hr_b4']}</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t["hr_btn"], type="primary", use_container_width=True):
                go("hr_intake")

    st.markdown(
        f"""
        <div class="sr-steps">
          <div class="sr-step"><em>📄</em><b>{t['step1']}</b><span>{t['step1s']}</span></div>
          <div class="sr-step"><em>📈</em><b>{t['step2']}</b><span>{t['step2s']}</span></div>
          <div class="sr-step"><em>🎯</em><b>{t['step3']}</b><span>{t['step3s']}</span></div>
          <div class="sr-step"><em>🛣️</em><b>{t['step4']}</b><span>{t['step4s']}</span></div>
        </div>
        <div class="sr-foot"><span class="sr-pulse"></span>{t['foot']}</div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Screen: jobseeker intake
# --------------------------------------------------------------------------- #

def screen_js_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    st.subheader(t["intake_h"])
    st.caption(t["intake_sub"])

    st.markdown(f'<div class="sr-pill">{t["opt_a"]}</div>', unsafe_allow_html=True)
    up = st.file_uploader(t["uploader"], type=["txt", "md", "pdf"])
    if up is not None:
        found = cv_to_skills(up)
        st.session_state["skills"] = found
        if found:
            st.success(t["detected"].format(len(found), ", ".join(found)))
        else:
            st.warning(t["not_detected"])
    st.caption(t["uploader_hint"])

    st.markdown(f'<div class="sr-pill">{t["opt_b"]}</div>', unsafe_allow_html=True)
    picked: list[str] = []
    lang = st.session_state.get("lang", "en")
    for group, items in TAXONOMY.items():
        st.markdown(f"**{cat(lang, group)}**")
        labels = st.multiselect(
            group, options=list(items), key=f"ms_{group}",
            label_visibility="collapsed", placeholder=t["ms_placeholder"],
        )
        for label in labels:
            picked += LABEL_TO_KEYS[label]
        st.markdown("")
    if st.button(t["use_skills"], use_container_width=True):
        st.session_state["skills"] = picked

    current = st.session_state.get("skills") or []
    if current:
        st.info(f"**{t['current']}:** {', '.join(sorted(set(current)))}  ({len(set(current))})")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button(t["back"], use_container_width=True):
            reset()
    with c2:
        if st.button(t["continue"], type="primary", use_container_width=True, disabled=not current):
            go("js_results")


# --------------------------------------------------------------------------- #
# Screen: jobseeker results
# --------------------------------------------------------------------------- #

def screen_js_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    skills = st.session_state.get("skills") or []
    if not skills:
        st.warning(t["not_detected"])
        if st.button(t["back"]):
            go("js_intake")
        return

    trend = load_trend()
    roles = apply_trend(load_roles(), trend)

    st.subheader(t["p1"])
    st.write(", ".join(sorted(set(skills))))

    st.subheader(t["p2"])
    trend_cards(t, trend)

    st.subheader(t["p3"])
    scenario = st.radio(
        t["scenario"], ["moderate", "fast"], horizontal=True,
        format_func=lambda x: t["moderate"] if x == "moderate" else t["fast"],
    )
    results = rank(skills, roles, scenario=scenario)
    st.caption(t["ranked_note"])
    for i, r in enumerate(results[:4]):
        role_card(t, r, expanded=(i == 0))

    st.subheader(t["p4"])
    top = results[0]
    if top["missing"]:
        total_required = len(top["covered"]) + len(top["missing"])
        st.write(t["gap"].format(top["role"], len(top["missing"]), total_required))
        plan = pathway(top)
        st.table([
            {"step": p["step"], "skill": p["skill"], "weeks": p["weeks"],
             "resource": t["search_hint"].format(p["skill"])}
            for p in plan
        ])
        st.caption(t["path_note"])
    else:
        st.success(t["covered_all"])

    st.subheader(t["p5"])
    summary = sdg_summary(results[:4])
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in summary.items()) or "—")
    st.caption(t["sdg_note"])

    st.subheader(t["p6"])
    st.dataframe(
        [{t["col_role"]: m["role"], t["col_mod"]: m["score"], t["col_fast"]: f["score"],
          t["col_delta"]: round(f["score"] - m["score"], 1)}
         for m, f in zip(rank(skills, roles, "moderate"), rank(skills, roles, "fast"))],
        use_container_width=True, hide_index=True,
    )
    st.caption(t["scen_note"])


# --------------------------------------------------------------------------- #
# Screen: HR intake
# --------------------------------------------------------------------------- #

def screen_hr_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    st.subheader(t["hr_h"])
    st.caption(t["hr_sub"])

    roster: dict[str, int] = {}
    for r in load_roles():
        n = st.slider(r.name, 0, 20, 1 if r.name.startswith("AI Operations") else 0)
        if n:
            roster[r.name] = n

    st.caption(t["hr_tip"])
    if st.button(t["analyse"], type="primary", use_container_width=True, disabled=not roster):
        st.session_state["roster"] = roster
        go("hr_results")
    if st.button(t["back"]):
        reset()


# --------------------------------------------------------------------------- #
# Screen: HR results
# --------------------------------------------------------------------------- #

def screen_hr_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    roster: dict[str, int] = st.session_state.get("roster") or {}
    if not roster:
        st.warning(t["hr_h"])
        if st.button(t["back"]):
            go("hr_intake")
        return

    trend = load_trend()
    roles = {r.name: r for r in apply_trend(load_roles(), trend)}
    total_people = sum(roster.values())

    st.subheader(t["hr_h"])
    a, b, c = st.columns(3)
    a.metric(t["people"], total_people)
    b.metric(t["roles"], len(roster))
    demand: dict[str, int] = {}
    for name, n in roster.items():
        for s in roles[name].required_skills:
            demand[s] = demand.get(s, 0) + n
    c.metric(t["skills"], len(demand))

    st.subheader(t["priority"])
    st.caption(t["priority_note"])
    st.dataframe(
        [{t["col_skill"]: s, t["col_people"]: n,
          t["col_share"]: f"{n / max(total_people, 1) * 100:.0f}%"}
         for s, n in sorted(demand.items(), key=lambda kv: -kv[1])],
        use_container_width=True, hide_index=True,
    )

    st.subheader(t["role_view"])
    for name, n in roster.items():
        role = roles[name]
        with st.expander(f"{name} · {n} · SDG {', '.join(role.sdg)}"):
            st.write(f"**{t['required']}:** {', '.join(role.required_skills)}")
            sig = "rising" if role.trend > 0.3 else "declining" if role.trend < -0.2 else "stable"
            st.write(f"**{t['signal']}:** {t.get(sig, sig)}")
            st.caption(t["agg_note"])

    st.subheader(t["plan"])
    plan = []
    for i, (s, n) in enumerate(sorted(demand.items(), key=lambda kv: -kv[1])[:5], start=1):
        plan.append({t["col_pri"]: i, t["col_skill"]: s, t["col_people"]: n,
                     t["col_route"]: t["search_hint"].format(s)})
    st.table(plan)
    st.caption(t["plan_note"])

    st.subheader(t["team_sdg"])
    sdg: dict[str, int] = {}
    for name in roster:
        for tag in roles[name].sdg:
            sdg[tag] = sdg.get(tag, 0) + 1
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in sorted(sdg.items(), key=lambda kv: -kv[1])))

    st.caption(t["hr_foot"])


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="SkillRadar MY", page_icon="📡", layout="wide")

st.session_state.setdefault("lang", "en")
play_intro()

STAGES = {
    "landing": screen_landing,
    "js_intake": screen_js_intake,
    "js_results": screen_js_results,
    "hr_intake": screen_hr_intake,
    "hr_results": screen_hr_results,
}

st.session_state.setdefault("stage", "landing")

STAGE = current_stage()
_T = T(st.session_state.get("lang", "en"))

if STAGE != "landing":
    st.markdown(APP_CSS, unsafe_allow_html=True)

try:
    STAGES.get(STAGE, screen_landing)()
except Exception as exc:  # keep the user on the screen with a readable message
    st.error(_T["error"])
    st.caption(f"{type(exc).__name__}: {exc}")
    if st.button(_T["back_start"]):
        reset()
