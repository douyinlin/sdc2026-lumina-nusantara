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
from i18n import STRINGS, T, cat, role_label, skill_label  # noqa: E402

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

ROLE_META: dict[str, dict] = {}

FIELD_DOMAIN: dict[str, str] = {}   # filled from FIELD_TO_DOMAIN at start-up

# Which neighbouring domains are still a credible move from each field.
ADJACENT = {
    "health": ["education", "business"],
    "it": ["business", "engineering"],
    "business": ["it", "law"],
    "engineering": ["it", "business"],
    "education": ["design", "business"],
    "design": ["business", "education"],
    "hospitality": ["business", "education"],
    "law": ["business"],
    "science": ["health", "education"],
}


def load_roles() -> list[Role]:
    """Load the curated catalogue (data/roles.json) with domain metadata."""
    path = DATA / "roles.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        roles = []
        ROLE_META.clear()
        for r in raw["roles"]:
            skills = [s if isinstance(s, str) else s["skill"] for s in r.get("skills", r.get("required_skills", []))]
            tiers = {s if isinstance(s, str) else s["skill"]: (None if isinstance(s, str) else s.get("tier", "important"))
                     for s in r.get("skills", [])}
            role = Role(r["name"], skills, r["trend"], r["sdg"], {k: v for k, v in tiers.items() if v})
            roles.append(role)
            ROLE_META[r["name"]] = {
                "domain": r.get("domain", "business"),
                "level": r.get("level", "mid"),
                "malaysia": r.get("malaysia", {}),
            }
        return roles
    except Exception:
        for r in DEFAULT_ROLES:
            ROLE_META[r.name] = {"domain": "business", "level": "mid"}
        return DEFAULT_ROLES


def roles_for_field(roles: list[Role], field: str) -> tuple[list[Role], list[Role]]:
    """Split roles into (same field, adjacent field) for a study field."""
    primary = FIELD_DOMAIN.get(field, "business")
    near = ADJACENT.get(primary, [])
    same, adjacent = [], []
    for r in roles:
        dom = ROLE_META.get(r.name, {}).get("domain", "business")
        if dom == primary:
            same.append(r)
        elif dom in near:
            adjacent.append(r)
    return same, adjacent


def load_trend() -> dict:
    try:
        return json.loads(TREND_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"is_simulated": True, "source_url": None, "retrieved_at": None,
                "note": "Simulated weights for demonstration.", "signals": []}


def _signal_strength(sig: dict) -> float:
    """Turn either a simulated weight or a real % change into a -1..1 signal."""
    if "weight" in sig:
        return float(sig["weight"])
    pct = sig.get("change_pct")
    if pct is None:
        return 0.0
    # +50% or more -> +1.0 ; -50% or worse -> -1.0 ; scaled linearly in between
    return max(-1.0, min(1.0, float(pct) / 50.0))


def apply_trend(roles: list[Role], trend: dict) -> list[Role]:
    """Blend the curated role trend with the live skill signals."""
    signals = trend.get("signals") or []
    out = []
    for role in roles:
        relevant = [_signal_strength(s) for s in signals if s["skill"] in (role.required_skills or [])]
        delta = sum(relevant) / len(relevant) if relevant else 0.0
        blended = 0.5 * role.trend + 0.5 * delta
        out.append(
            Role(
                role.name,
                role.required_skills,
                max(-1.0, min(1.0, blended)),
                role.sdg,
                dict(role.tiers),
            )
        )
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
    options = ["en", "ms", "zh"]
    labels = {"en": "English", "ms": "Bahasa Malaysia", "zh": "中文"}
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


TREND_CSS = """
<style>
.tr-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin:6px 0 4px; }
.tr-card { background:rgba(255,255,255,.82); border:1px solid rgba(255,255,255,.95);
           border-radius:16px; padding:14px 16px 12px; box-shadow:0 10px 26px rgba(76,86,52,.10);
           border-left:5px solid #9aa88b; }
.tr-card.up { border-left-color:#5f8f3f; }
.tr-card.down { border-left-color:#c0504d; }
.tr-card.flat { border-left-color:#9aa0a6; }
.tr-skill { font-size:19px; font-weight:750; color:#33401f; line-height:1.25;
            letter-spacing:-.2px; margin-bottom:2px; }
.tr-dir { font-size:14px; font-weight:600; margin-bottom:8px; }
.tr-card.up .tr-dir { color:#4a7a2f; }
.tr-card.down .tr-dir { color:#b2403d; }
.tr-card.flat .tr-dir { color:#6b7075; }
.tr-badge { display:inline-block; padding:3px 10px; border-radius:999px;
            font-size:12.5px; font-weight:650; }
.tr-card.up .tr-badge { background:rgba(95,143,63,.14); color:#3f6b26; }
.tr-card.down .tr-badge { background:rgba(192,80,77,.14); color:#9d3532; }
.tr-card.flat .tr-badge { background:rgba(120,126,131,.14); color:#5c6165; }
</style>
"""


DOSM_CSS = """
<style>
.ds-wrap { background:rgba(255,255,255,.9); border:1px solid rgba(138,154,91,.28);
           border-radius:18px; padding:16px 18px 10px; margin:4px 0 14px;
           box-shadow:0 12px 30px rgba(76,86,52,.10); }
.ds-head { display:flex; justify-content:space-between; align-items:baseline; gap:12px;
           border-bottom:1px solid rgba(138,154,91,.22); padding-bottom:9px; margin-bottom:10px; }
.ds-title { font-size:15.5px; font-weight:750; color:#33401f; }
.ds-src { font-size:11.5px; color:#7a836a; }
.ds-total { font-size:13px; color:#4a5a2a; font-weight:600; margin-bottom:10px; }
.ds-total b { font-size:19px; }
.ds-row { display:flex; align-items:center; gap:10px; margin-bottom:7px; }
.ds-name { flex:0 0 300px; font-size:12.5px; color:#3f4a26; }
.ds-bar { flex:1; height:10px; background:rgba(138,154,91,.14); border-radius:6px; overflow:hidden; }
.ds-fill { height:100%; border-radius:6px;
           background:linear-gradient(90deg,#8A9A5B,#5b7fa6); }
.ds-num { flex:0 0 130px; text-align:right; font-size:12px; font-variant-numeric:tabular-nums;
          color:#33401f; font-weight:650; }
.ds-up { color:#4a7a2f; font-weight:700; }
.ds-down { color:#b2403d; font-weight:700; }
.ds-flat { color:#6b7075; font-weight:700; }
.ds-note { font-size:11px; color:#8a927e; margin-top:8px; }
</style>
"""


def _fmt(n: int) -> str:
    return f"{n:,}"


RADAR_CSS = """
<style>
.rd-legend { font-size: 11.5px; color:#6b7560; margin-top:2px; }
.rd-legend b { color:#4a5a2a; }
</style>
"""


def dosm_radar(t: dict, d: dict) -> None:
    """Radar of the official DOSM occupational counts (current vs previous quarter)."""
    occ = d.get("occupations_q2_2025") or []
    if len(occ) < 3:
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        return

    labels = [o["group"] for o in occ]
    cur = [o["offers"] for o in occ]
    prev = [o.get("offers_prev") or 0 for o in occ]

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    cur_c = cur + cur[:1]
    prev_c = prev + prev[:1]

    fig, ax = plt.subplots(figsize=(3.9, 3.6), subplot_kw=dict(polar=True), dpi=170)
    ax.set_facecolor("none")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles, prev_c, color="#b7c1a5", linewidth=1.3, label=f"2025 Q1")
    ax.fill(angles, prev_c, color="#b7c1a5", alpha=0.18)
    ax.plot(angles, cur_c, color="#5b7fa6", linewidth=1.9, label=f"2025 Q2")
    ax.fill(angles, cur_c, color="#5b7fa6", alpha=0.25)
    ax.scatter(angles[:-1], cur, color="#5b7fa6", s=16, zorder=5)

    short = [l.replace(" and Associate Professionals", " & Assc. Prof.")
              .replace(" and Chief Executives", " & CEOs")
              .replace(" and Marketing Professionals", " & Marketing")
              .replace(" and Auditors", " & Auditors")
              .replace("Administrative Professionals", "Admin Professionals")
             for l in labels]
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(short, fontsize=6.4, color="#3f4a26")
    ax.set_yticklabels([])
    ax.tick_params(axis="x", pad=6)
    ax.grid(color="#d8dfca", linewidth=0.7)
    ax.spines["polar"].set_color("#e2e8d8")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, fontsize=7.4, handlelength=1.4, columnspacing=1.2)
    fig.patch.set_alpha(0)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def dosm_panel(t: dict, lang: str) -> None:
    """Layer 1 — the official DOSM online-vacancy counts, untouched."""
    path = DATA / "trends" / "dosm_q2_2025.json"
    if not path.exists():
        return
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return

    st.markdown(DOSM_CSS, unsafe_allow_html=True)
    total = d.get("total", {})
    occ = d.get("occupations_q2_2025", [])
    if not occ:
        return
    peak = max(o["offers"] for o in occ)

    rows = []
    for o in occ:
        prev = o.get("offers_prev") or 0
        chg = ((o["offers"] - prev) / prev * 100) if prev else None
        if chg is None:
            arrow, cls = "•", "ds-flat"
            chg_txt = "—"
        elif chg > 5:
            arrow, cls = "▲", "ds-up"
            chg_txt = f"+{chg:.1f}%"
        elif chg < -5:
            arrow, cls = "▼", "ds-down"
            chg_txt = f"{chg:.1f}%"
        else:
            arrow, cls = "▬", "ds-flat"
            chg_txt = f"{chg:+.1f}%"
        width = o["offers"] / peak * 100
        rows.append(
            '<div class="ds-row">'
            f'<div class="ds-name">{o["group"]}</div>'
            f'<div class="ds-bar"><div class="ds-fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="ds-num">{_fmt(o["offers"])} <span class="{cls}">{arrow} {chg_txt}</span></div>'
            "</div>"
        )

    st.markdown(
        '<div class="ds-wrap">'
        '<div class="ds-head">'
        f'<div class="ds-title">🇲🇾 {t["dosm_title"]}</div>'
        f'<div class="ds-src">{t["dosm_source"]} · {d.get("latest_period")} · {d.get("latest_released")}</div>'
        "</div>"
        f'<div class="ds-total">{t["dosm_total"]}: <b>{_fmt(total.get("q2_2025", 0))}</b> '
        f'({t["dosm_qoq"]} {total.get("qoq_pct", 0):+.1f}%)</div>'
        + f'<div class="ds-note">📄 <a href="{d.get("latest_url", "")}" target="_blank">{t["view_source"]}</a>'
          f' · {t["prev_quarter"]}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    # radar of the same official numbers — compact, beside the figures
    st.markdown(RADAR_CSS, unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="medium")
    with left:
        st.markdown(f"**{t['radar_title']}**")
        st.caption(t["radar_note"].format(d.get("latest_period"), d.get("previous_period")))
        dosm_radar(t, d)
    with right:
        st.markdown(f"**{t['radar_values']}**")
        body_rows = []
        for o in (d.get("occupations_q2_2025") or []):
            prev = o.get("offers_prev") or 0
            chg = ((o["offers"] - prev) / prev * 100) if prev else 0.0
            cls = "ds-up" if chg > 5 else ("ds-down" if chg < -5 else "ds-flat")
            body_rows.append(
                "<tr>"
                f"<td style='padding:5px 8px;border-bottom:1px solid #eef0e8'>{o['group']}</td>"
                f"<td style='padding:5px 8px;text-align:right;border-bottom:1px solid #eef0e8;"
                f"font-variant-numeric:tabular-nums'>{_fmt(prev)}</td>"
                f"<td style='padding:5px 8px;text-align:right;border-bottom:1px solid #eef0e8;"
                f"font-variant-numeric:tabular-nums;font-weight:650'>{_fmt(o['offers'])}</td>"
                f"<td style='padding:5px 8px;text-align:right;border-bottom:1px solid #eef0e8' "
                f"class='{cls}'>{chg:+.1f}%</td>"
                "</tr>"
            )
        st.markdown(
            "<table style='width:100%;border-collapse:collapse;font-size:12px;color:#3f4a26'>"
            "<thead><tr>"
            f"<th style='text-align:left;padding:6px 8px;border-bottom:1px solid #cfd8c0'>{t['col_occ']}</th>"
            "<th style='text-align:right;padding:6px 8px;border-bottom:1px solid #cfd8c0'>2025 Q1</th>"
            "<th style='text-align:right;padding:6px 8px;border-bottom:1px solid #cfd8c0'>2025 Q2</th>"
            f"<th style='text-align:right;padding:6px 8px;border-bottom:1px solid #cfd8c0'>{t['dosm_qoq']}</th>"
            "</tr></thead><tbody>"
            + "".join(body_rows)
            + "</tbody></table>",
            unsafe_allow_html=True,
        )
        st.caption(t["radar_footnote"])


def trend_cards(t: dict, trend: dict, lang: str = "en") -> None:
    """Layer 2 — skill directions derived from the official counts above."""
    dosm_panel(t, lang)

    if not trend.get("is_simulated", True):
        st.caption(
            f"**{t['derived_from']}** · {t['source']}: {trend.get('source')} "
            f"(retrieved {trend.get('retrieved_at')})"
        )
    else:
        st.caption(
            "**" + t["simulated"] + "** · " + t["source"] + ": "
            + str(trend.get("source_url") or "—")
        )

    signals = trend.get("signals") or []
    if not signals:
        st.info("—")
        return

    st.markdown(TREND_CSS, unsafe_allow_html=True)
    cls = {"rising": ("up", "📈"), "declining": ("down", "📉"), "stable": ("flat", "➖")}
    cards = []
    for sig in signals[:6]:
        kind, icon = cls.get(sig["direction"], ("flat", "•"))
        if "change_pct" in sig:
            badge = f'{_fmt(sig["offers"])} · {sig["change_pct"]:+.1f}%'
        else:
            badge = t["weight"].format("{:+.1f}".format(sig.get("weight", 0)))
        title = skill_label(lang, str(sig["skill"]))
        basis = sig.get("basis", "")
        cards.append(
            '<div class="tr-card ' + kind + '" title="' + basis.replace('"', "'") + '">'
            + '<div class="tr-skill">' + title + '</div>'
            + '<div class="tr-dir">' + icon + " " + t.get(sig["direction"], sig["direction"]) + '</div>'
            + '<span class="tr-badge">' + badge + '</span>'
            + '</div>'
        )
    st.markdown('<div class="tr-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
    st.caption(t["hover_basis"])



def role_card(t: dict, result: dict, expanded: bool = False, lang: str = "en") -> None:
    c = result["components"]
    head = f"{result['score']:.1f} · {role_label(lang, result['role'])} · SDG {', '.join(result['sdg'])}"
    with st.expander(head, expanded=expanded):
        st.progress(min(1.0, result["score"] / 100))
        a, b, c1, d, e = st.columns(5)
        a.metric(t["coverage"], f"{c['coverage'] * 100:.0f}%")
        b.metric(t["focus"], f"{c.get('focus', 0) * 100:.0f}%")
        c1.metric(t["transfer"], f"{c['transfer'] * 100:.0f}%")
        d.metric(t["trend"], f"{c['trend'] * 100:.0f}%")
        e.metric(t["gapcost"], f"{c['gap_cost'] * 100:.0f}%")
        have = ", ".join(skill_label(lang, x) for x in result["covered"]) or "—"
        close_items = []
        for x in result["missing"]:
            tier = result.get("tiers", {}).get(x)
            tag = f" ({t['tier_' + tier]})" if tier else ""
            close_items.append(skill_label(lang, x) + tag)
        close = ", ".join(close_items) or t["none"]
        total = len(result["covered"]) + len(result["missing"])
        pct = round(100 * len(result["covered"]) / total) if total else 0
        st.caption(t["why_score"].format(total, len(result["covered"]), pct))
        st.write(f"**{t['have']} ({len(result['covered'])}):** {have}")
        st.write(f"**{t['close']} ({len(result['missing'])}):** {close}")

        my = ROLE_META.get(result["role"], {}).get("malaysia") or {}
        if my:
            lvl = my.get("shortage", "")
            badge = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(lvl, "•")
            st.markdown(
                f"{badge} **{t['my_demand']}: {t.get('short_' + lvl, lvl)}** · "
                f"{my.get('note', '')}  \n"
                f"<span style='font-size:12px;color:#7a836a'>📄 {my.get('source', '')} "
                f"({my.get('published', '')}) · <a href='{my.get('source_url', '')}' target='_blank'>"
                f"{t['view_source']}</a></span>",
                unsafe_allow_html=True,
            )
        st.caption(t["estimate"])


# --------------------------------------------------------------------------- #
# Screen: landing (three entry points)
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
          <div class="sr-sub">{t['hero_sub']}<br>
            <span style="font-size:13px;color:#7a836a">{t['hero_note']}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown(
                f"""<div class="sr-icon">👤</div><div class="sr-title">{t['p1_title']}</div>
                <div class="sr-desc">{t['p1_desc']}</div>
                <ul class="sr-list"><li>📄 {t['p1_b1']}</li><li>📈 {t['p1_b2']}</li>
                <li>🎯 {t['p1_b3']}</li></ul>""",
                unsafe_allow_html=True,
            )
            if st.button(t["p1_btn"], type="primary", use_container_width=True):
                go("js_intake")
    with c2:
        with st.container(border=True):
            st.markdown(
                f"""<div class="sr-icon">🏢</div><div class="sr-title">{t['p2_title']}</div>
                <div class="sr-desc">{t['p2_desc']}</div>
                <ul class="sr-list"><li>👥 {t['p2_b1']}</li><li>🔥 {t['p2_b2']}</li>
                <li>💸 {t['p2_b3']}</li></ul>""",
                unsafe_allow_html=True,
            )
            if st.button(t["p2_btn"], type="primary", use_container_width=True):
                go("hr_intake")
    with c3:
        with st.container(border=True):
            st.markdown(
                f"""<div class="sr-icon">🎓</div><div class="sr-title">{t['p3_title']}</div>
                <div class="sr-desc">{t['p3_desc']}</div>
                <ul class="sr-list"><li>🏫 {t['p3_b1']}</li><li>📚 {t['p3_b2']}</li>
                <li>🌱 {t['p3_b3']}</li></ul>""",
                unsafe_allow_html=True,
            )
            if st.button(t["p3_btn"], type="primary", use_container_width=True):
                go("cc_intake")

    st.markdown(
        f"""<div class="sr-step" style="max-width:900px;margin:18px auto 0">
        <b>{t['flow']}</b><span>{t['flow_s']}</span></div>
        <div class="sr-foot"><span class="sr-pulse"></span>{t['foot']}</div>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Screen: jobseeker intake — two personas
# --------------------------------------------------------------------------- #

def screen_js_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    st.subheader(t["intake_h"])

    persona = st.radio(
        t["persona_q"], ["worker", "grad"], horizontal=True,
        format_func=lambda k: t["persona_worker"] if k == "worker" else t["persona_grad"],
    )
    st.session_state["persona"] = persona

    st.markdown(f'<div class="sr-pill">{t["persona_ctx"]}</div>', unsafe_allow_html=True)

    if persona == "worker":
        c1, c2 = st.columns(2)
        with c1:
            st.session_state["years"] = st.slider(t["q_years"], 0, 30, 6)
            st.session_state["urgency"] = st.selectbox(
                t["q_urgency"], ["now", "6m", "12m"],
                format_func=lambda k: t["urg_" + k],
            )
        with c2:
            st.session_state["hours"] = st.slider(t["q_hours"], 1, 20, 8)
            st.session_state["budget"] = st.selectbox(
                t["q_budget"], ["low", "mid", "high"],
                format_func=lambda k: t["bud_" + k],
            )
        st.caption(t["worker_note"])
    else:
        c1, c2 = st.columns(2)
        with c1:
            _edu_options = ["diploma", "bachelor", "master", "phd"]
            st.session_state["edu"] = st.selectbox(
                t["q_edu"],
                _edu_options,
                index=_edu_options.index(st.session_state.get("edu", "bachelor"))
                if st.session_state.get("edu") in _edu_options else 1,
                format_func=lambda k: t["edu_" + k],
            )
            _group = st.selectbox(t["q_field"], list(FIELDS))
            st.session_state["field"] = st.selectbox(
                t["q_field_detail"], FIELDS[_group], label_visibility="visible"
            )
        with c2:
            st.session_state["intern"] = st.slider(t["q_intern"], 0, 12, 0)
            st.session_state["grad_year"] = st.selectbox(t["q_grad_year"], [2026, 2027, 2028])
        st.session_state["hours"] = st.slider(t["q_hours"], 1, 20, 10)
        st.caption(t["grad_note"])

    st.divider()
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
            max_selections=6,
        )
        for label in labels:
            picked += LABEL_TO_KEYS[label]
        st.markdown("")
    if st.button(t["use_skills"], use_container_width=True):
        st.session_state["skills"] = picked

    current = st.session_state.get("skills") or []
    if current:
        st.info(f"**{t['current']}:** {', '.join(sorted(set(current)))}  ({len(set(current))})")
        if len(set(current)) > 10:
            st.caption(t["too_many"])

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button(t["back"], use_container_width=True):
            reset()
    with c2:
        if st.button(t["continue"], type="primary", use_container_width=True, disabled=not current):
            go("js_results")


# --------------------------------------------------------------------------- #
# Screen: jobseeker results — persona aware
# --------------------------------------------------------------------------- #

def screen_js_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    skills = st.session_state.get("skills") or []
    persona = st.session_state.get("persona", "worker")
    if not skills:
        st.warning(t["not_detected"])
        if st.button(t["back"]):
            go("js_intake")
        return

    trend = load_trend()
    all_roles = apply_trend(load_roles(), trend)
    hours = st.session_state.get("hours", 8)
    scale = 8.0 / max(hours, 1)

    # Domain-aware filtering: never recommend a role from an unrelated field.
    field = st.session_state.get("field", "Business")
    raw_profile = st.session_state.get("skills") or skills
    # keep only skills the catalogue knows about (drop anything typed via an old key)
    known = {sk for r in all_roles for sk in r.required_skills}
    skills = [sk for sk in raw_profile if sk in known] or raw_profile
    same, adjacent = roles_for_field(all_roles, field)
    pool = same if same else adjacent
    if not pool:
        pool = all_roles
    roles = pool

    st.subheader(t["p1"])
    st.write(", ".join(sorted(set(skills))))
    if persona == "worker":
        st.caption(t["ctx_worker"].format(
            st.session_state.get("years", 0), t["urg_" + st.session_state.get("urgency", "now")]
        ))
    else:
        st.caption(t["ctx_grad"].format(
            t["edu_" + st.session_state.get("edu", "bachelor")],
            st.session_state.get("field", "—"),
            st.session_state.get("intern", 0),
        ))

    st.subheader(t["p2"])
    trend_cards(t, trend, st.session_state.get('lang', 'en'))

    st.subheader(t["p3"])
    scenario = st.radio(
        t["scenario"], ["moderate", "fast"], horizontal=True,
        format_func=lambda x: t["moderate"] if x == "moderate" else t["fast"],
    )
    results = rank(skills, roles, scenario=scenario)

    # persona-specific advice banner
    if persona == "worker":
        top1 = results[0]
        gap_n = len(top1["missing"])
        if gap_n <= 2:
            st.success(t["adv_worker_fast"].format(role_label(st.session_state.get("lang", "en"), top1["role"])))
        else:
            st.info(t["adv_worker_slow"].format(role_label(st.session_state.get("lang", "en"), top1["role"]), gap_n))
    else:
        intern = st.session_state.get("intern", 0)
        if intern < 3:
            st.warning(t["adv_grad_intern"])
        else:
            st.success(t["adv_grad_ok"].format(intern))

    lang_now = st.session_state.get("lang", "en")
    if same:
        st.caption(t["domain_same"].format(field, len(same)))
    else:
        st.caption(t["domain_adjacent"].format(field))
    st.caption(t["ranked_note"])
    st.caption(t["role_source"])
    roles_by_name = {x.name: x for x in roles}
    for i, r in enumerate(results[:4]):
        dom = ROLE_META.get(r["role"], {}).get("domain", "")
        badge = t["badge_same"] if dom == FIELD_DOMAIN.get(field) else t["badge_adjacent"]
        if i == 0:
            st.caption(badge)
        r["tiers"] = {sk: roles_by_name.get(r["role"], Role(r["role"], [], 0)).tier_of(sk) for sk in r["missing"]}
        role_card(t, r, expanded=(i == 0), lang=lang_now)

    st.subheader(t["p4"])
    top = results[0]
    if top["missing"]:
        total_required = len(top["covered"]) + len(top["missing"])
        st.write(t["gap"].format(role_label(st.session_state.get("lang", "en"), top["role"]),
                                  len(top["missing"]), total_required))
        plan = pathway(top)
        rows = []
        for p in plan:
            weeks = max(1, round(p["weeks"] * scale))
            rows.append({
                t["step"]: p["step"], t["skill"]: p["skill"],
                t["weeks"]: weeks,
                t["resource"]: t["search_hint"].format(skill_label(st.session_state.get("lang", "en"), p["skill"])),
            })
        st.table(rows)
        st.caption(t["path_note"].format(hours))
    else:
        st.success(t["covered_all"])

    with st.expander(t["disclose_title"]):
        st.markdown(t["disclose_body"])

    st.subheader(t["p5"])
    summary = sdg_summary(results[:4])
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in summary.items()) or "—")
    st.caption(t["sdg_note"])

    st.subheader(t["p6"])
    moderate_rank = rank(skills, roles, "moderate")
    fast_rank = rank(skills, roles, "fast")
    pos_m = {r["role"]: i + 1 for i, r in enumerate(moderate_rank)}
    pos_f = {r["role"]: i + 1 for i, r in enumerate(fast_rank)}
    score_m = {r["role"]: r["score"] for r in moderate_rank}
    score_f = {r["role"]: r["score"] for r in fast_rank}

    lang_s = st.session_state.get("lang", "en")
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown(f"**{t['scen_moderate_label']}**")
        for i, r in enumerate(moderate_rank[:5], start=1):
            st.markdown(
                f"{i}. {role_label(lang_s, r['role'])} — **{r['score']}**",
                unsafe_allow_html=True,
            )
    with col_b:
        st.markdown(f"**{t['scen_fast_label']}**")
        for i, r in enumerate(fast_rank[:5], start=1):
            before = pos_m.get(r["role"], 99)
            delta = before - i
            if delta > 0:
                mark = f"<span style='color:#4a7a2f;font-weight:700'> ▲{delta}</span>"
            elif delta < 0:
                mark = f"<span style='color:#b2403d;font-weight:700'> ▼{abs(delta)}</span>"
            else:
                mark = "<span style='color:#8a927e'> –</span>"
            st.markdown(f"{i}. {role_label(lang_s, r['role'])} — **{r['score']}**{mark}",
                        unsafe_allow_html=True)

    with st.expander(t["scen_detail"]):
        st.dataframe(
            [
                {
                    t["col_role"]: role_label(lang_s, r["role"]),
                    t["col_mod"]: score_m.get(r["role"], 0),
                    t["col_fast"]: score_f.get(r["role"], 0),
                    t["col_delta"]: round(score_f.get(r["role"], 0) - score_m.get(r["role"], 0), 1),
                    t["col_pos"]: f"#{pos_m.get(r['role'], '-')} → #{pos_f.get(r['role'], '-')}",
                }
                for r in moderate_rank
            ],
            use_container_width=True,
            hide_index=True,
        )
    st.caption(t["scen_note"])


# --------------------------------------------------------------------------- #
# Screen: HR intake / results
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

    roles = {r.name: r for r in apply_trend(load_roles(), load_trend())}
    total_people = sum(roster.values())
    demand: dict[str, int] = {}
    for name, n in roster.items():
        for s in roles[name].required_skills:
            demand[s] = demand.get(s, 0) + n

    st.subheader(t["hr_h"])
    a, b, c = st.columns(3)
    a.metric(t["people"], total_people)
    b.metric(t["roles"], len(roster))
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
# Screen: career centre (TVET / university) intake / results
# --------------------------------------------------------------------------- #

def screen_cc_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    st.subheader(t["cc_h"])
    st.caption(t["cc_sub"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state["prog"] = st.text_input(t["cc_prog"], "Diploma in Business Administration")
    with c2:
        st.session_state["cohort"] = st.slider(t["cc_cohort"], 5, 500, 60)
    with c3:
        st.session_state["cyear"] = st.selectbox(t["cc_year"], [2026, 2027, 2028])

    roles = load_roles()
    targets = st.multiselect(
        t["cc_targets"], options=[r.name for r in roles],
        default=[r.name for r in roles[:2]],
    )
    st.session_state["targets"] = targets

    if targets:
        needed = sorted({s for r in roles if r.name in targets for s in r.required_skills})
        taught = st.multiselect(t["cc_taught"], options=needed, default=needed[:2])
        st.session_state["taught"] = taught

        if st.button(t["cc_run"], type="primary", use_container_width=True):
            go("cc_results")

    if st.button(t["back"]):
        reset()


def screen_cc_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    targets = st.session_state.get("targets") or []
    taught = st.session_state.get("taught") or []
    if not targets:
        st.warning(t["cc_h"])
        if st.button(t["back"]):
            go("cc_intake")
        return

    roles = {r.name: r for r in apply_trend(load_roles(), load_trend())}
    needed = sorted({s for r in roles.values() if r.name in targets for s in r.required_skills})
    covered = [s for s in needed if s in taught]
    missing = [s for s in needed if s not in taught]
    coverage = len(covered) / len(needed) if needed else 0

    st.subheader(t["cc_overview"])
    a, b, c = st.columns(3)
    a.metric(t["cc_prog_lbl"], st.session_state.get("prog", "—"))
    b.metric(t["cc_cohort_lbl"], st.session_state.get("cohort", 0))
    c.metric(t["coverage"], f"{coverage * 100:.0f}%")

    st.subheader(t["cc_curriculum"])
    st.caption(t["cc_curriculum_note"].format(len(covered), len(needed)))
    st.dataframe(
        [{t["col_skill"]: s, t["cc_status"]: t["cc_have"] if s in covered else t["cc_miss"]}
         for s in needed],
        use_container_width=True, hide_index=True,
    )

    st.subheader(t["cc_add"])
    if missing:
        st.table([
            {t["col_pri"]: i, t["col_skill"]: s, t["col_route"]: t["search_hint"].format(s)}
            for i, s in enumerate(missing[:6], start=1)
        ])
    else:
        st.success(t["cc_complete"])

    st.subheader(t["cc_roles"])
    st.dataframe(
        [{"Role": r.name, "SDG": ", ".join(r.sdg),
          "Trend": t.get("rising" if r.trend > 0.3 else "declining" if r.trend < -0.2 else "stable"),
          "Required skills": len(r.required_skills)}
         for r in roles.values() if r.name in targets],
        use_container_width=True, hide_index=True,
    )

    st.subheader(t["team_sdg"])
    sdg: dict[str, int] = {}
    for r in roles.values():
        if r.name in targets:
            for tag in r.sdg:
                sdg[tag] = sdg.get(tag, 0) + 1
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in sorted(sdg.items(), key=lambda kv: -kv[1])))
    st.caption(t["cc_foot"])


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="SkillRadar MY", page_icon="📡", layout="wide")

st.session_state.setdefault("lang", "en")
play_intro()

# Grouped so the list is scannable; the label shown is "GROUP — Field".
FIELDS: dict[str, list[str]] = {
    "Business & Finance": [
        "Accounting / Finance", "Business Administration", "Marketing",
        "Human Resource Management", "Economics", "Entrepreneurship",
    ],
    "Computing & Data": [
        "Computer Science", "Software Engineering", "Information Systems",
        "Data Science / Analytics", "Cybersecurity", "Artificial Intelligence",
    ],
    "Engineering": [
        "Mechanical Engineering", "Electrical / Electronic Engineering",
        "Civil Engineering", "Chemical Engineering", "Industrial Engineering",
        "Mechatronics / Robotics",
    ],
    "Health & Life Sciences": [
        "Medicine / MBBS", "Nursing", "Pharmacy", "Dentistry",
        "Biomedical Science", "Public Health", "Physiotherapy",
    ],
    "Education & Social": [
        "Education / Teaching", "Psychology", "Social Work",
        "Communication / Media", "Law",
    ],
    "Design & Media": [
        "Graphic Design", "UI / UX Design", "Multimedia / Animation",
        "Film & Broadcasting",
    ],
    "Hospitality & Tourism": [
        "Hotel Management", "Culinary Arts", "Tourism Management",
    ],
    "Sciences & Environment": [
        "Biology", "Chemistry", "Physics", "Environmental Science",
        "Agriculture / Food Science",
    ],
    "Built Environment & Other": [
        "Architecture", "Quantity Surveying", "Logistics / Supply Chain",
        "Other",
    ],
}

# field -> catalogue domain used for filtering
FIELD_TO_DOMAIN: dict[str, str] = {
    "Accounting / Finance": "business", "Business Administration": "business",
    "Marketing": "business", "Human Resource Management": "business",
    "Economics": "business", "Entrepreneurship": "business",
    "Computer Science": "it", "Software Engineering": "it", "Information Systems": "it",
    "Data Science / Analytics": "it", "Cybersecurity": "it", "Artificial Intelligence": "it",
    "Mechanical Engineering": "engineering", "Electrical / Electronic Engineering": "engineering",
    "Civil Engineering": "engineering", "Chemical Engineering": "engineering",
    "Industrial Engineering": "engineering", "Mechatronics / Robotics": "engineering",
    "Medicine / MBBS": "health", "Nursing": "health", "Pharmacy": "health",
    "Dentistry": "health", "Biomedical Science": "health", "Public Health": "health",
    "Physiotherapy": "health",
    "Education / Teaching": "education", "Psychology": "education", "Social Work": "education",
    "Communication / Media": "design", "Law": "law",
    "Graphic Design": "design", "UI / UX Design": "design",
    "Multimedia / Animation": "design", "Film & Broadcasting": "design",
    "Hotel Management": "hospitality", "Culinary Arts": "hospitality",
    "Tourism Management": "hospitality",
    "Biology": "science", "Chemistry": "science", "Physics": "science",
    "Environmental Science": "science", "Agriculture / Food Science": "science",
    "Architecture": "engineering", "Quantity Surveying": "engineering",
    "Logistics / Supply Chain": "engineering", "Other": "business",
}

FIELD_DOMAIN.update(FIELD_TO_DOMAIN)

STAGES = {
    "landing": screen_landing,
    "js_intake": screen_js_intake,
    "js_results": screen_js_results,
    "hr_intake": screen_hr_intake,
    "hr_results": screen_hr_results,
    "cc_intake": screen_cc_intake,
    "cc_results": screen_cc_results,
}

st.session_state.setdefault("stage", "landing")

STAGE = current_stage()
_T = T(st.session_state.get("lang", "en"))

if STAGE != "landing":
    st.markdown(APP_CSS, unsafe_allow_html=True)

try:
    STAGES.get(STAGE, screen_landing)()
except Exception as exc:
    st.error(_T["error"])
    st.caption(f"{type(exc).__name__}: {exc}")
    if st.button(_T["back_start"]):
        reset()
