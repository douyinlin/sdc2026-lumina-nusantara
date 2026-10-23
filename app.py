"""SkillRadar MY — guided application.

Flow:  landing (choose who you are)  ->  intake (full screen)  ->  results
       * Jobseeker: CV upload or categorised questionnaire -> matches, gap, pathway, SDG
       * HR: team roster -> workforce gap heatmap, priority gaps, reskilling plan

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
import base64
import hashlib
import re
import sys
import zlib
from urllib.parse import quote_plus
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from utils import normalize_skills, GAP_COST, TRANSFERABILITY, Role, pathway, rank, sdg_summary  # noqa: E402
from i18n import CATEGORY_LABELS, ROLE_PARENTHETICAL, SKILL_PARENTHETICAL, STRINGS, T, cat, role_label, skill_label  # noqa: E402
from src.cv import cv_to_skills
from src.planning import filter_roles, learning_duration
from src.trends import read_snapshot, update_status, apply_trend, _signal_strength, snapshot_signals, signal_key
from functools import partial
from typing import cast
from labels import field_label, group_label, skill_option_label  # noqa: E402
from presentation import CSS_PATH, brand, copy_for, flow_header, learning_path, logo_mark, score_panel, skill_chips  # noqa: E402

# Copy lives in data/i18n/*.json, not in Python modules, because Streamlit keeps
# imported modules alive across reruns and redeploys: a redeploy would otherwise
# keep serving the old tables (this shipped a KeyError to the live demo twice).
# app.py is re-executed on every run, so the merge happens here, every time.
I18N_DATA = ROOT / "data" / "i18n"


def _load_copy(name: str) -> dict:
    try:
        return json.loads((I18N_DATA / name).read_text(encoding="utf-8"))
    except Exception:
        return {}


for _lang, _extra in _load_copy("decision_copy.json").items():
    STRINGS.setdefault(_lang, {}).update(_extra)
for _lang, _names in _load_copy("role_names.json").items():
    ROLE_PARENTHETICAL.setdefault(_lang, {}).update(_names)
for _lang, _cats in _load_copy("categories.json").items():
    CATEGORY_LABELS.setdefault(_lang, {}).update(_cats)

DATA = ROOT / "data"

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
    "🏗 Engineering & Built Environment": {
        "CAD / technical drawing (AutoCAD, SolidWorks)": ["cad"],
        "Structural analysis & design": ["structural analysis"],
        "Site supervision & construction management": ["site supervision"],
        "Quantity surveying & cost estimation": ["quantity surveying"],
        "BIM (Revit) & building services": ["bim"],
        "Electrical systems & wiring": ["electrical systems"],
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


SKILL_SDG_FILE = DATA / "skills_sdg.json"


def load_skill_sdg() -> dict:
    """Team-curated skill -> SDG targets; see the note inside the file."""
    try:
        return json.loads(SKILL_SDG_FILE.read_text(encoding="utf-8")).get("skills", {})
    except Exception:
        return {}

def load_courses() -> dict[str, dict]:
    """Existing course records; durations remain unverified unless documented."""
    path = DATA / "courses.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return {c["skill"]: c for c in raw.get("courses", [])}
    except Exception:
        return {}


def _loc(row: dict, field: str, lang: str = "en") -> str:
    """Localized variant of a data field, falling back to English."""
    if lang and lang != "en":
        value = row.get(f"{field}_{lang}")
        if value:
            return value
    return row.get(field) or ""


#: English display names for acronym skills; the raw keys are lowercase.
SKILL_DISPLAY = {
    "sql": "SQL", "python": "Python", "excel": "Excel", "cad": "CAD", "bim": "BIM",
    "ui ux": "UI/UX", "osh": "OSH", "it support": "IT support", "hr operations": "HR operations",
    "crm administration": "CRM administration", "ai": "AI", "llm": "LLM",
}

#: In Chinese and Malay prose, these are better known by their English name than
#: by a literal gloss ("结构化查询" means nothing to the person we are writing for).
SKILL_PLAIN_OVERRIDE = {
    "zh": {"sql": "SQL", "python": "Python", "excel": "Excel", "cad": "CAD", "bim": "BIM",
           "ui ux": "UI/UX", "osh": "OSH", "it support": "IT 支持", "ai": "AI"},
    "ms": {"sql": "SQL", "python": "Python", "excel": "Excel", "cad": "CAD", "bim": "BIM",
           "ui ux": "UI/UX", "osh": "OSH", "ai": "AI"},
}


def skill_plain(lang: str, key: str) -> str:
    """One name only — for sentences. Tables keep the English so people can match
    it against a job ad; a sentence with four brackets is unreadable."""
    if lang == "en":
        return SKILL_DISPLAY.get(key, key)
    override = SKILL_PLAIN_OVERRIDE.get(lang, {}).get(key)
    if override:
        return override
    return SKILL_PARENTHETICAL.get(lang, {}).get(key) or key


def role_plain(lang: str, name: str) -> str:
    if lang == "en":
        return name
    return ROLE_PARENTHETICAL.get(lang, {}).get(name) or name




#: Named-skill signals carry a direction but no published percentage, so each one
#: moves the trend by a fixed amount instead of an invented number.
NAMED_SIGNAL_WEIGHT = 0.7


def _named_skill_snapshot() -> dict:
    """Layer 2 as a standalone signal source (direction only, no percentages)."""
    path = DATA / "trends" / "jobstreet_skills_2025.json"
    try:
        d = read_snapshot(path)
    except (ValueError, OSError) as exc:
        raise ValueError("Jobstreet snapshot unavailable; repair or import a valid snapshot") from exc
    signals = snapshot_signals(d, NAMED_SIGNAL_WEIGHT)
    return {
        "kind": "jobstreet",
        "scenario": False,
        "observed": True,
        "forecast": False,
        "is_simulated": False,
        "signals": signals,
        "source": d.get("source"),
        "source_zh": d.get("source_zh"),
        "source_ms": d.get("source_ms"),
        "source_url": d.get("source_url"),
        "retrieved_at": d.get("retrieved_at"),
        "published": d.get("published"),
    }


WEF_SIGNAL_WEIGHT = 0.7


def _wef_skill_snapshot() -> dict:
    """WEF skills outlook through 2030; broad categories map only when stated."""
    path = DATA / "trends" / "wef_future_jobs_2025.json"
    try:
        d = read_snapshot(path)
    except (ValueError, OSError) as exc:
        raise ValueError("WEF snapshot unavailable; repair or import a valid snapshot") from exc
    signals = snapshot_signals(d, WEF_SIGNAL_WEIGHT)
    return {
        "kind": "wef",
        "scenario": False,
        "observed": False,
        "forecast": True,
        "is_simulated": False,
        "signals": signals,
        "source": d.get("source"),
        "source_url": d.get("source_url"),
        "source_zh": d.get("source_zh"),
        "source_ms": d.get("source_ms"),
        "retrieved_at": d.get("retrieved_at"),
        "published": d.get("published"),
        "horizon": d.get("horizon"),
        "scope": d.get("scope"),
        "scoring_note": d.get("scoring_note"),
    }


def load_snapshot(kind: str = "wef") -> dict:
    """One skill-evidence source; DOSM occupation counts stay a separate panel."""
    status = update_status(DATA / "trends", kind)
    t = T(st.session_state.get("lang", "en"))
    st.caption(t["snapshot_note"])
    if status.get("ok") is False:
        st.warning(t["update_failed"])
    if kind == "jobstreet":
        return _named_skill_snapshot()
    return _wef_skill_snapshot()






# --------------------------------------------------------------------------- #
# Motion — one-time portal entry and a 0.7s transition on stage changes.
# The entry gate does not own or alter the app's later routes.
# --------------------------------------------------------------------------- #

ANIM_CSS = """
<style>
@keyframes sr-curtain {
  0%   { opacity: 1; }
  88%  { opacity: 1; }
  100% { opacity: 0; visibility: hidden; }
}
/* The panel fades out before the backdrop does, so the intro headline never
   sits on top of the landing headline during the cross-fade. */
@keyframes sr-curtain-out {
  0%, 68% { opacity: 1; }
  82%     { opacity: 0; }
  100%    { opacity: 0; }
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
.sr-curtain-inner {
  max-width: 860px; padding: 0 28px;
  animation: sr-curtain-out 2.2s ease forwards;
}
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
<style>
.sr-intro { position:fixed; inset:0; z-index:999990; overflow:hidden; display:grid; place-items:center; color:#eafaff; isolation:isolate; background:#07111c; }
.sr-scene-frame { position:relative; width:min(100vw,177.78vh); height:min(100vh,56.25vw); aspect-ratio:16/9; overflow:hidden; isolation:isolate; transform-origin:50% 42%; transform:translate3d(0,0,0); backface-visibility:hidden; box-shadow:0 30px 90px rgba(0,0,0,.3); }
.sr-scene-image { position:absolute; inset:0; background-size:cover; background-position:center; transition:opacity 2.8s cubic-bezier(.2,.65,.25,1); }
.sr-scene-day { background-image:url('/app/static/landing-day.jpg'); opacity:0; }
.sr-scene-night { background-image:url('/app/static/landing-rain-night.jpg'); opacity:1; }
.sr-scene-frame[data-time-of-day='day'] .sr-scene-day { opacity:1; }
.sr-scene-frame[data-time-of-day='day'] .sr-scene-night { opacity:0; }
.sr-scene-frame:after { content:""; position:absolute; z-index:2; inset:0; pointer-events:none; background:linear-gradient(180deg,rgba(4,12,20,.4),transparent 19%,transparent 75%,rgba(4,12,20,.15)); }
.sr-rain-pane { position:absolute; z-index:3; overflow:hidden; pointer-events:none; opacity:.78; transition:opacity 2s ease; }
.sr-scene-frame[data-time-of-day='day'] .sr-rain-pane { opacity:.42; }
.sr-rain-pane canvas { width:100%; height:100%; display:block; }
.sr-rain-top { left:34%; top:0; width:66%; height:21.5%; }
.sr-rain-right { left:72%; top:21%; width:28%; height:43%; }
.sr-intro-top { position:absolute; z-index:4; top:max(12px,calc(50% - min(50vh,28.125vw) + 16px)); left:max(16px,calc(50% - min(50vw,88.89vh) + 24px)); right:max(16px,calc(50% - min(50vw,88.89vh) + 24px)); display:flex; justify-content:space-between; align-items:center; color:rgba(245,250,255,.92); font:600 10px/1.4 ui-monospace,Consolas,monospace; letter-spacing:.15em; text-transform:uppercase; text-shadow:0 2px 12px rgba(0,0,0,.65); pointer-events:none; }
.sr-intro-brand { display:inline-flex; align-items:center; gap:8px; font:800 13px/1.2 'Helvetica Neue',Arial,sans-serif; letter-spacing:.13em; }
.sr-intro-logo { width:26px; height:26px; flex:none; filter:drop-shadow(0 1px 8px rgba(93,235,203,.24)); }
.sr-intro-clock { font-variant-numeric:tabular-nums; }
.sr-intro-heading { position:absolute; z-index:4; top:calc(50% - min(50vh,28.125vw) + 10px); left:50%; transform:translateX(-50%); color:#f1fbff; font-size:clamp(11px,1.2vw,15px); font-weight:600; letter-spacing:.15em; text-transform:uppercase; text-shadow:0 2px 14px rgba(0,0,0,.7); text-align:center; white-space:nowrap; pointer-events:none; }
body:has(.sr-intro:not(.sr-intro-zoom)) [data-testid="stHeader"],body:has(.sr-intro:not(.sr-intro-zoom)) [data-testid="stToolbar"],body:has(.sr-intro:not(.sr-intro-zoom)) footer { display:none !important; }
body:has(.sr-intro:not(.sr-intro-zoom)) [data-testid="stMainBlockContainer"] { max-width:none !important; padding:0 !important; }
body:has(.sr-intro:not(.sr-intro-zoom)) [data-testid="stAppViewContainer"] { overflow:hidden !important; }
.sr-scene-cta { position:absolute; z-index:5; left:50%; top:54%; transform:translate(-50%,-50%); padding:9px 15px; border:1px solid rgba(138,239,244,.82); border-radius:5px; color:#e9ffff; background:rgba(11,35,48,.78); box-shadow:0 0 22px rgba(67,226,235,.2); font:700 10px/1.2 ui-monospace,Consolas,monospace; letter-spacing:.16em; white-space:nowrap; cursor:pointer; transition:opacity .22s ease; }
.sr-scene-cta:focus-visible { outline:2px solid #b3f5eb; outline-offset:4px; }
.sr-intro.sr-intro-zoom .sr-scene-cta { opacity:0; pointer-events:none; }
.st-key-intro_zoom_continue { position:fixed !important; z-index:-1 !important; width:1px !important; height:1px !important; overflow:hidden !important; opacity:0 !important; pointer-events:none !important; }
.st-key-intro_zoom_continue button { width:1px !important; height:1px !important; min-height:0 !important; padding:0 !important; }
@media(max-width:640px) { .sr-intro-top { font-size:8px; top:calc(50% - min(50vh,28.125vw) + 8px); left:12px; right:12px; } .sr-intro-brand { font-size:10px; } .sr-intro-heading { top:calc(50% - min(50vh,28.125vw) + 28px); font-size:9px; } .sr-scene-cta { font-size:8px; padding:7px 10px; } }
@media(prefers-reduced-motion:reduce) { .sr-scene-image,.sr-rain-pane { transition:none !important; } }
</style>
<div class="sr-intro" aria-label="SkillRadar MY entry screen">
  <div class="sr-scene-frame" data-time-of-day="night" aria-hidden="true">
    <div class="sr-scene-image sr-scene-day"></div><div class="sr-scene-image sr-scene-night"></div>
    <div class="sr-rain-pane sr-rain-top"><canvas></canvas></div><div class="sr-rain-pane sr-rain-right"><canvas></canvas></div>
  </div>
  <div class="sr-intro-top"><span class="sr-intro-brand">SKILLRADAR MY</span><span class="sr-intro-clock">LOCAL TIME · --:--</span></div>
  <div class="sr-intro-heading">A clearer path to your next role</div>
  <button class="sr-scene-cta" type="button">CLICK TO ENTER</button>
</div>
"""
INTRO_HTML = INTRO_HTML.replace(
    '<span class="sr-intro-brand">SKILLRADAR MY</span>',
    f'<span class="sr-intro-brand">{logo_mark("sr-intro-logo")}<span>SKILLRADAR MY</span></span>',
)


def _scene_data_uri(filename: str) -> str:
    """Inline the intro artwork so the landing scene does not depend on a static route."""
    image_path = ROOT / "static" / filename
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


INTRO_HTML = INTRO_HTML.replace(
    "url('/app/static/landing-day.jpg')",
    f"url('{_scene_data_uri('landing-day.jpg')}')",
).replace(
    "url('/app/static/landing-rain-night.jpg')",
    f"url('{_scene_data_uri('landing-rain-night.jpg')}')",
)

INTRO_SCENE_CONTROLLER = """
<script>
(() => {
  const w = window.parent, d = w.document;
  const hostFrame = window.frameElement;
  if (hostFrame) {
    Object.assign(hostFrame.style, {position:"fixed",width:"0",height:"0",left:"0",top:"0",border:"0",visibility:"hidden",pointerEvents:"none"});
    const wrapper = hostFrame.closest('[data-testid="stElementContainer"]');
    if (wrapper) Object.assign(wrapper.style, {position:"fixed",width:"0",height:"0",margin:"0",padding:"0",overflow:"hidden",pointerEvents:"none",zIndex:"-1"});
  }
  let attempts = 0;
  function mount() {
    const intro = d.querySelector(".sr-intro");
    if (!intro) { if (++attempts < 80) w.setTimeout(mount, 40); return; }
    const frame = intro.querySelector(".sr-scene-frame");
    const clock = intro.querySelector(".sr-intro-clock");
    function syncLocalTime() {
      const now = new Date();
      const hour = now.getHours();
      const mode = hour >= 6 && hour < 18 ? "day" : "night";
      frame.dataset.timeOfDay = mode;
      if (clock) clock.textContent = `LOCAL TIME · ${now.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})} · ${mode.toUpperCase()}`;
    }
    syncLocalTime();
    const timer = w.setInterval(syncLocalTime, 60000);
    const cta = intro.querySelector(".sr-scene-cta");
    if (cta && !cta.dataset.zoomBound) {
      cta.dataset.zoomBound = "true";
      cta.addEventListener("click", () => {
        if (intro.classList.contains("sr-intro-zoom")) return;
        intro.classList.add("sr-intro-zoom");
        const reducedMotion = w.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const deadline = Date.now() + 12000;
        function continueToWebIntro() {
          const button = d.querySelector(".st-key-intro_zoom_continue button");
          if (button) button.click();
          else if (Date.now() < deadline) w.setTimeout(continueToWebIntro, 50);
        }
        w.setTimeout(continueToWebIntro, reducedMotion ? 40 : 3050);
      }, {once:true});
    }
    const panes = [...intro.querySelectorAll(".sr-rain-pane")].map((pane, index) => {
      const canvas = pane.querySelector("canvas");
      const ctx = canvas.getContext("2d");
      let width = 1, height = 1, drops = [], last = 0;
      function resize() {
        const rect = pane.getBoundingClientRect();
        const ratio = Math.min(w.devicePixelRatio || 1, 1.5);
        width = Math.max(1, rect.width); height = Math.max(1, rect.height);
        canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
        ctx.setTransform(ratio,0,0,ratio,0,0);
        const count = index === 0 ? Math.max(10, Math.round(width / 20)) : Math.max(12, Math.round(height / 11));
        drops = Array.from({length:count}, () => ({x:Math.random()*width,y:Math.random()*height,len:8+Math.random()*20,speed:180+Math.random()*300,drift:-24-Math.random()*35,alpha:.15+Math.random()*.42}));
      }
      function draw(time) {
        if (intro.classList.contains("sr-intro-zoom")) { ctx.clearRect(0,0,width,height); return; }
        const dt = Math.min(.04, Math.max(0, (time-last)/1000 || .016)); last = time;
        ctx.clearRect(0,0,width,height);
        for (const p of drops) {
          if (!w.matchMedia("(prefers-reduced-motion: reduce)").matches) { p.y += p.speed*dt; p.x += p.drift*dt; }
          if (p.y > height+p.len || p.x < -8) { p.x=Math.random()*width; p.y=-p.len; }
          const g=ctx.createLinearGradient(p.x,p.y-p.len,p.x+2,p.y);
          g.addColorStop(0,`rgba(205,235,255,0)`); g.addColorStop(1,`rgba(205,235,255,${p.alpha})`);
          ctx.strokeStyle=g; ctx.lineWidth=.8; ctx.beginPath(); ctx.moveTo(p.x,p.y-p.len); ctx.lineTo(p.x+2,p.y); ctx.stroke();
        }
        if (!w.matchMedia("(prefers-reduced-motion: reduce)").matches) pane.raf=w.requestAnimationFrame(draw);
      }
      resize(); pane.onresize=resize; draw(0);
      return pane;
    });
    const resizeAll = () => panes.forEach(pane => pane.onresize && pane.onresize());
    const cleanup = () => { w.clearInterval(timer); w.removeEventListener("resize",resizeAll); for (const pane of panes) w.cancelAnimationFrame(pane.raf); };
    if (w.__skillRadarIntroCleanup) w.__skillRadarIntroCleanup();
    w.__skillRadarIntroCleanup = cleanup;
    w.addEventListener("resize", resizeAll);
  }
  mount();
})();
</script>
"""

ENTRY_REVEAL_CSS = """
<style>
@keyframes sr-portal-reveal { from { opacity:0; } to { opacity:1; } }
[data-testid="stAppViewContainer"] { animation:sr-portal-reveal .45s ease-out both; }
@media(prefers-reduced-motion:reduce) { [data-testid="stAppViewContainer"] { animation:none !important; } }
</style>
"""

LEGACY_INTRO_HTML = """
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

ENTRY_TRANSITION_CSS = """
<style>
@keyframes sr-entry-scene-fade {
  0%, 87% { opacity:1; }
  100% { opacity:0; visibility:hidden; }
}
@keyframes sr-entry-camera-push {
  /* Dense samples of a smooth ease-in/ease-out curve keep the camera motion continuous. */
  0% { transform:translate3d(0,0,0) scale(1); opacity:1; }
  10% { transform:translate3d(0,0,0) scale(1.023); opacity:1; }
  20% { transform:translate3d(0,0,0) scale(1.085); opacity:1; }
  30% { transform:translate3d(0,0,0) scale(1.174); opacity:1; }
  40% { transform:translate3d(0,0,0) scale(1.279); opacity:1; }
  50% { transform:translate3d(0,0,0) scale(1.39); opacity:1; }
  60% { transform:translate3d(0,0,0) scale(1.501); opacity:1; }
  70% { transform:translate3d(0,0,0) scale(1.606); opacity:1; }
  80% { transform:translate3d(0,0,0) scale(1.695); opacity:1; }
  90% { transform:translate3d(0,0,0) scale(1.757); opacity:1; }
  97% { transform:translate3d(0,0,0) scale(1.78); opacity:1; }
  100% { transform:translate3d(0,0,0) scale(1.79); opacity:0; }
}
.sr-intro.sr-intro-zoom {
  animation:sr-entry-scene-fade 3s cubic-bezier(.4,0,.2,1) forwards;
  pointer-events:none;
  will-change:opacity;
}
.sr-intro.sr-intro-zoom .sr-scene-frame {
  animation:sr-entry-camera-push 3s linear forwards;
  will-change:transform,opacity; transform:translate3d(0,0,0); backface-visibility:hidden;
}
.sr-intro.sr-intro-zoom .sr-intro-top,
.sr-intro.sr-intro-zoom .sr-intro-heading {
  animation:sr-entry-scene-fade .75s ease forwards;
}
.sr-intro.sr-intro-zoom .sr-rain-pane {
  opacity:0;
  transition:opacity .25s ease;
}
.sr-intro.sr-intro-zoom .sr-intro-clock {
  animation:sr-entry-scene-fade .35s ease forwards;
}
@media(prefers-reduced-motion:reduce) {
  .sr-intro.sr-intro-zoom,.sr-intro.sr-intro-zoom .sr-scene-frame { animation-duration:.001ms !important; animation-delay:0s !important; }
}
</style>
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

def render_particle_field() -> None:
    """Render a cursor-reactive particle layer across the app viewport."""
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] { isolation:isolate; }
          [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"] {
            position:relative;
            z-index:1;
          }
          /* Every element container sits at z-index 1, so paint order falls back to
             DOM order — the particle layer is rendered after the intro curtain and
             would cover it. Lift the curtain itself above the field. */
          [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(.sr-curtain) {
            z-index: 4;
          }
          [data-testid="stHeader"], [data-testid="stSidebar"] {
            position:relative;
            z-index:2;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.iframe(
        """
        <style>
          html, body { width:100%; height:100%; margin:0; overflow:hidden; background:transparent; }
          #particle-scene { position:fixed; inset:0; width:100vw; height:100vh; overflow:hidden; pointer-events:none; }
          canvas { display:block; width:100%; height:100%; }
        </style>
        <div id="particle-scene" aria-hidden="true"></div>
        <script>
          const root = document.getElementById("particle-scene");
          const parentWindow = window.parent;
          const parentDocument = parentWindow.document;
          const reducedMotion = parentWindow.matchMedia("(prefers-reduced-motion: reduce)").matches;
          const canvas = document.createElement("canvas");
          const ctx = canvas.getContext("2d");
          root.appendChild(canvas);
          const frame = window.frameElement;
          const view = parentDocument.querySelector('[data-testid="stAppViewContainer"]');
          const pointer = { x:-1000, y:-1000, active:false, strength:0 };
          const colors = ["211, 185, 255", "255, 255, 255", "181, 138, 231", "168, 185, 160"];
          const particles = [];
          const trail = [];
          let width = 1, height = 1, raf = 0;

          if (parentWindow.__skillRadarParticleCleanup) {
            parentWindow.__skillRadarParticleCleanup();
          }

          if (frame) {
            frame.title = "SkillRadar full-page cursor particle field";
            Object.assign(frame.style, {
              position:"fixed", inset:"0", width:"100vw", height:"100vh",
              maxWidth:"none", border:"0", pointerEvents:"none", zIndex:"0"
            });
            let wrapper = frame.parentElement;
            while (wrapper && wrapper !== parentDocument.body &&
              wrapper.getAttribute("data-testid") !== "stElementContainer") {
              wrapper = wrapper.parentElement;
            }
            if (wrapper && wrapper !== parentDocument.body) {
              Object.assign(wrapper.style, {
                position:"fixed", inset:"0", width:"100vw", height:"100vh",
                margin:"0", padding:"0", pointerEvents:"none", zIndex:"0", overflow:"hidden"
              });
            }
          }
          if (view) view.style.isolation = "isolate";

          function resize() {
            const dpr = Math.min(parentWindow.devicePixelRatio || 1, 1.5);
            width = Math.max(1, parentWindow.innerWidth);
            height = Math.max(1, parentWindow.innerHeight);
            canvas.width = Math.round(width * dpr);
            canvas.height = Math.round(height * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            particles.length = 0;
            const count = Math.min(520, Math.round(width * height / 1800));
            for (let i = 0; i < count; i++) {
              const x = Math.random() * width, y = Math.random() * height;
              particles.push({ x, y, homeX:x, homeY:y, vx:0, vy:0,
                radius:.7 + Math.random() * 1.7,
                color:colors[Math.floor(Math.random() * colors.length)],
                alpha:.24 + Math.random() * .48, phase:Math.random() * Math.PI * 2 });
            }
          }

          function movePointer(event) {
            const x = event.clientX, y = event.clientY;
            if (pointer.active && !reducedMotion) {
              const dx = x - pointer.x, dy = y - pointer.y;
              const distance = Math.hypot(dx, dy);
              const pieces = Math.min(8, Math.ceil(distance / 12));
              for (let i = 0; i < pieces; i++) {
                const t = (i + 1) / (pieces + 1);
                trail.push({ x:pointer.x + dx * t, y:pointer.y + dy * t,
                  vx:(Math.random() - .5) * 1.5, vy:(Math.random() - .5) * 1.5,
                  life:1, radius:.8 + Math.random() * 2.1,
                  color:colors[Math.floor(Math.random() * colors.length)] });
              }
            }
            pointer.x = x; pointer.y = y; pointer.active = true; pointer.strength = 1;
            if (reducedMotion) drawStatic();
          }

          function drawStatic() {
            ctx.clearRect(0, 0, width, height);
            for (const p of particles) {
              ctx.fillStyle = `rgba(${p.color}, ${p.alpha})`;
              ctx.beginPath(); ctx.arc(p.homeX, p.homeY, p.radius, 0, Math.PI * 2); ctx.fill();
            }
            if (pointer.active) drawGlow(0.38);
          }

          function drawGlow(amount) {
            const radius = Math.max(110, Math.min(width, height) * .25);
            const glow = ctx.createRadialGradient(pointer.x, pointer.y, 0,
              pointer.x, pointer.y, radius);
            glow.addColorStop(0, `rgba(255,255,255,${.56 * amount})`);
            glow.addColorStop(.35, `rgba(226,208,255,${.28 * amount})`);
            glow.addColorStop(1, "rgba(226,208,255,0)");
            ctx.fillStyle = glow;
            ctx.fillRect(pointer.x - radius, pointer.y - radius, radius * 2, radius * 2);
          }

          function introRunning() {
            const curtain = parentDocument.querySelector(".sr-curtain");
            if (!curtain) return false;
            const style = parentWindow.getComputedStyle(curtain);
            return style.visibility !== "hidden" && parseFloat(style.opacity || "1") > 0.02;
          }

          function render(time) {
            // The intro owns the screen while it is up: stay invisible instead of
            // drifting under/over its headline, then start once it is gone.
            if (introRunning()) {
              ctx.clearRect(0, 0, width, height);
              raf = requestAnimationFrame(render);
              return;
            }
            ctx.clearRect(0, 0, width, height);
            if (pointer.active) {
              drawGlow(pointer.strength);
              pointer.strength = Math.max(.30, pointer.strength * .992);
            }
            for (const p of particles) {
              const dx = p.x - pointer.x, dy = p.y - pointer.y;
              const distance = Math.hypot(dx, dy) || 1;
              if (pointer.active && distance < 130) {
                const force = (1 - distance / 130) * 1.05;
                p.vx += dx / distance * force;
                p.vy += dy / distance * force;
              }
              p.vx += (p.homeX - p.x) * .012;
              p.vy += (p.homeY - p.y) * .012;
              p.vx *= .91; p.vy *= .91;
              p.x += p.vx; p.y += p.vy;
              const twinkle = .76 + Math.sin(time * .0015 + p.phase) * .24;
              ctx.fillStyle = `rgba(${p.color}, ${p.alpha * twinkle})`;
              ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
            }
            for (let i = trail.length - 1; i >= 0; i--) {
              const p = trail[i];
              p.x += p.vx; p.y += p.vy; p.life -= .018;
              if (p.life <= 0) { trail.splice(i, 1); continue; }
              ctx.fillStyle = `rgba(${p.color}, ${p.life * .82})`;
              ctx.beginPath(); ctx.arc(p.x, p.y, p.radius * p.life, 0, Math.PI * 2); ctx.fill();
            }
            raf = requestAnimationFrame(render);
          }

          function handleBlur() { pointer.active = false; }
          function cleanup() {
            cancelAnimationFrame(raf);
            parentDocument.removeEventListener("pointermove", movePointer);
            parentWindow.removeEventListener("resize", resize);
            parentWindow.removeEventListener("blur", handleBlur);
            if (view) view.style.isolation = "";
            delete parentWindow.__skillRadarParticleCleanup;
          }
          parentWindow.__skillRadarParticleCleanup = cleanup;

          parentDocument.addEventListener("pointermove", movePointer, { passive:true });
          parentWindow.addEventListener("resize", resize, { passive:true });
          parentWindow.addEventListener("blur", handleBlur);
          resize();
          if (reducedMotion) drawStatic();
          else raf = requestAnimationFrame(render);
        </script>
        """,
        width="stretch",
        height=1,
        alt="SkillRadar full-page cursor particle field",
        tab_index=-1,
    )

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
/* a disabled primary button used to keep the green gradient while Streamlit
   dimmed only the inner label, so the text vanished into the background */
.stButton > button[kind="primary"]:disabled {
  background: #e3e8d8 !important; border: 1px solid #cfd8c0 !important;
  color: #6b7560 !important; box-shadow: none; transform: none;
  opacity: 1 !important; cursor: not-allowed;
}
.stButton > button[kind="primary"]:disabled p,
.stButton > button[kind="primary"]:disabled span,
.stButton > button[kind="primary"]:disabled div {
  color: #6b7560 !important;
}
.stButton > button[kind="primary"]:disabled:hover { transform: none; box-shadow: none; }

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
/* section-5 heading row (plain text; the toggle is a normal button below it) */
.sdg-head-row {
  display: flex; align-items: center;
  border-left: 4px solid #8A9A5B; padding-left: 10px;
  margin: 8px 0 2px; min-height: 34px;
}
.sdg-head-text { font-size: 1.5rem; font-weight: 700; color: #3f4a26; line-height: 1.2; }
.sr-pill { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px;
           color:#5d6b36; background:rgba(138,154,91,.14);
           border:1px solid rgba(138,154,91,.32); margin-bottom:8px; }
</style>
"""


def play_intro():
    """Run the push-in in the browser, then reveal the web intro after it ends."""
    if st.session_state.pop("_entry_web_intro_pending", False):
        st.markdown(ANIM_CSS + LEGACY_INTRO_HTML, unsafe_allow_html=True)
        return None

    if st.session_state.get("_entry_sequence_done"):
        return None

    st.markdown(INTRO_HTML + ENTRY_TRANSITION_CSS, unsafe_allow_html=True)
    st.iframe(INTRO_SCENE_CONTROLLER, height=1, width=1, tab_index=-1, alt="Local time and rain animation")
    if st.button("Continue to SkillRadar", key="intro_zoom_continue"):
        st.session_state["_entry_sequence_done"] = True
        st.session_state["intro_done"] = True
        st.session_state["_intro_reveal_pending"] = True
        st.session_state["_entry_web_intro_pending"] = True
        st.rerun()
    # Keep the underlying app and particle field out until the camera push ends.
    st.stop()


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
    st.iframe(SCROLL_JS, height=1, width=1, tab_index=-1, alt="Scroll position helper")


def screen_wrap() -> None:
    """Fade content in and reset scroll whenever the stage changes.

    The scroll reset must happen on *every* stage change, not only when the
    fade flag is set: otherwise clicking a button near the bottom of the
    landing page left the next screen scrolled halfway down.
    """
    # Keep the particle backdrop mounted for every app stage, including long
    # intake and results screens that scroll well below the initial viewport.
    render_particle_field()

    if st.session_state.pop("_intro_reveal_pending", False):
        st.markdown(ENTRY_REVEAL_CSS, unsafe_allow_html=True)

    stage = st.session_state.get("stage", "landing")
    if st.session_state.get("_scrolled_stage") != stage:
        st.session_state["_scrolled_stage"] = stage
        st.markdown(ANIM_CSS, unsafe_allow_html=True)
        scroll_top()


def go(stage: str) -> None:
    st.session_state["stage"] = stage
    st.session_state["entering"] = True
    st.rerun()


def reset() -> None:
    """Clear the answers but keep the language the user picked."""
    keep = {"intro_done", "_entry_sequence_done", "lang"}
    for k in list(st.session_state):
        if k not in keep:
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
        "Language / Bahasa / 语言",
        options=options,
        index=options.index(current),
        format_func=lambda k: labels[k],
        label_visibility="collapsed" if compact else "visible",
        key=f"lang_{'c' if compact else 'f'}",
    )
    if choice != current:
        st.session_state["lang"] = choice
        st.rerun()


STEP_ORDER = {"js_intake": 1, "js_results": 2, "hr_intake": 1, "hr_results": 2,
              "cc_intake": 1, "cc_results": 2}


def step_banner(t: dict) -> None:
    """Accessible, presentation-only journey progress after role selection."""
    stage = st.session_state.get("stage", "landing")
    human = {"js_intake": ("jobseeker", 2), "js_results": ("jobseeker", 2),
             "hr_intake": ("hr", 2), "hr_results": ("hr", 2),
             "cc_intake": ("cc", 2), "cc_results": ("cc", 2)}
    kind, _ = human.get(stage, ("jobseeker", 2))
    flow_key = {"jobseeker": "flow_jobseeker", "hr": "flow_hr", "cc": "flow_cc"}.get(kind)
    flow = t.get(flow_key, "") if flow_key else ""
    st.markdown(
        flow_header(stage, flow, st.session_state.get("lang", "en")),
        unsafe_allow_html=True,
    )


def top_bar(t: dict) -> None:
    left, right, far = st.columns([3, 1.5, 1.5])
    with left:
        st.markdown(brand(), unsafe_allow_html=True)
    with right:
        if st.button(t["reeval"], width="stretch", help=t["reeval_help"]):
            reset()
    with far:
        lang_selector(compact=True)


#: Official UN SDG colours for goals 1-17.
SDG_COLOURS = {
    1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
    6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
    11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
    16: "#00689D", 17: "#19486A",
}


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


def dosm_radar(t: dict, d: dict, lang: str = "en") -> None:
    """Radar of the official DOSM occupational counts (current vs previous quarter)."""
    occ = d.get("occupations") or []
    if len(occ) < 3:
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.projections.polar import PolarAxes
        import numpy as np
    except Exception:
        return

    labels = [_loc(o, "group", lang) for o in occ]
    cur = [o["offers"] for o in occ]
    prev = [o.get("offers_prev") or 0 for o in occ]

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    cur_c = cur + cur[:1]
    prev_c = prev + prev[:1]

    fig, ax = plt.subplots(figsize=(3.4, 3.2), subplot_kw=dict(polar=True), dpi=170)
    ax = cast(PolarAxes, ax)
    ax.set_facecolor("none")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles, prev_c, color="#b7c1a5", linewidth=1.2, label=d.get("previous_period", "Previous"))
    ax.fill(angles, prev_c, color="#b7c1a5", alpha=0.16)
    ax.plot(angles, cur_c, color="#5b7fa6", linewidth=1.7, label=d.get("latest_period", "Latest"))
    ax.fill(angles, cur_c, color="#5b7fa6", alpha=0.22)
    ax.scatter(angles[:-1], cur, color="#5b7fa6", s=13, zorder=5)

    # Matplotlib has no CJK font in this environment, so Chinese or Malay axis
    # labels render as empty boxes. Number the spokes instead and let the table
    # beside the chart act as the legend — the same numbers appear there.
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([str(i + 1) for i in range(n)], fontsize=8.0, color="#3f4a26")
    ax.set_yticklabels([])
    ax.tick_params(axis="x", pad=2)
    ax.grid(color="#d8dfca", linewidth=0.6)
    ax.spines["polar"].set_color("#e2e8d8")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.19), ncol=2, frameon=False,
              fontsize=6.8, handlelength=1.2, columnspacing=1.0)
    fig.patch.set_alpha(0)
    st.pyplot(fig, width="content")
    plt.close(fig)


def dosm_panel(t: dict, lang: str) -> None:
    """Layer 1 — official DOSM occupational demand (labelled as an occupational signal)."""
    path = DATA / "trends" / "dosm_q2_2026.json"
    if not path.exists():
        return
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    occ = d.get("occupations") or []
    if not occ:
        return

    st.markdown(DOSM_CSS, unsafe_allow_html=True)
    total = d.get("total", {})
    st.markdown(
        '<div class="ds-wrap">'
        '<div class="ds-head">'
        f'<div class="ds-title">🇲🇾 {t["dosm_title"]}</div>'
        f'<div class="ds-src">{t["dosm_source"]} · {d.get("latest_period")} · {d.get("latest_released")}</div>'
        "</div>"
        f'<div class="ds-total">{t["dosm_total"]}: <b>{_fmt(total.get("offers", 0))}</b> '
        f'({t["dosm_qoq"]} {total.get("qoq_pct", 0):+.1f}%)</div>'
        f'<div class="ds-note">{t["occ_layer_note"]}</div>'
        f'<div class="ds-note">{t["occ_scope_note"]}</div>'
        f'<div class="ds-note">📄 <a href="{d.get("source_url", "")}" target="_blank">{t["view_source"]}</a>'
        f' · {t["prev_quarter"]}</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 2], gap="medium")
    with left:
        st.markdown(f"**{t['radar_title']}**")
        dosm_radar(t, d, lang)
    with right:
        st.markdown(f"**{t['radar_values']}**")
        body_rows = []
        for idx, o in enumerate(occ, start=1):
            prev = o.get("offers_prev") or 0
            chg = ((o["offers"] - prev) / prev * 100) if prev else 0.0
            cls = "ds-up" if chg > 5 else ("ds-down" if chg < -5 else "ds-flat")
            row_style = "padding:4px 8px;border-bottom:1px solid #eef0e8"
            num_style = (f"{row_style};text-align:right;color:#8a9478;"
                         "font-variant-numeric:tabular-nums;width:1.6em")
            body_rows.append(
                "<tr>"
                f"<td style='{num_style}'>{idx}</td>"
                f"<td style='{row_style}'>{_loc(o, 'group', lang)}</td>"
                f"<td style='{row_style};text-align:right;font-variant-numeric:tabular-nums'>{_fmt(prev)}</td>"
                f"<td style='{row_style};text-align:right;font-variant-numeric:tabular-nums;font-weight:650'>"
                f"{_fmt(o['offers'])}</td>"
                f"<td style='{row_style};text-align:right' class='{cls}'>{chg:+.1f}%</td>"
                "</tr>"
            )
        head_style = "padding:5px 8px;border-bottom:1px solid #cfd8c0"
        st.markdown(
            "<table style='width:100%;border-collapse:collapse;font-size:11.5px;color:#3f4a26'>"
            "<thead><tr>"
            f"<th style='{head_style};text-align:right'>#</th>"
            f"<th style='{head_style};text-align:left'>{t['col_occ']}</th>"
            f"<th style='{head_style};text-align:right'>{d.get('previous_period', '')}</th>"
            f"<th style='{head_style};text-align:right'>{d.get('latest_period', '')}</th>"
            f"<th style='{head_style};text-align:right'>{t['dosm_qoq']}</th>"
            "</tr></thead><tbody>" + "".join(body_rows) + "</tbody></table>",
            unsafe_allow_html=True,
        )
        moves = [((o["offers"] - (o.get("offers_prev") or 0)) / (o.get("offers_prev") or 1) * 100)
                 for o in occ if o.get("offers_prev")]
        # A quarter where every group fell looks like a broken table unless the page
        # says so; the release itself reported a broad decline.
        if moves and all(m < 0 for m in moves):
            st.caption(t["radar_footnote"].format(previous=d.get("previous_period", ""))
                       + " " + t["all_down_note"].format(n=len(moves)))
        else:
            st.caption(t["radar_footnote"].format(previous=d.get("previous_period", "")))
        st.caption(t["radar_index_note"])


def skill_evidence_panel(t: dict, lang: str) -> None:
    """Layer 2 — skills the cited article names directly, with the proxy caveat stated."""
    path = DATA / "trends" / "jobstreet_skills_2025.json"
    if not path.exists():
        return
    try:
        d = read_snapshot(path)
    except Exception:
        return

    st.markdown(f"### {t['skill_layer_title']}")
    st.caption(
        f"**{t['skill_layer_note']}** · {_loc(d, 'source', lang)} · {d.get('published')} · "
        f"[{t['view_source']}]({d.get('source_url')})"
    )

    # headline facts from the same article
    facts = d.get("headline_facts") or []
    if facts:
        st.markdown("**" + t["facts_title"] + "**")
        for f in facts:
            st.markdown(f"- {_loc(f, 'fact', lang)}")
        st.markdown("")

    signals = d.get("skill_signals") or []
    if signals:
        st.markdown(TREND_CSS, unsafe_allow_html=True)
        cls = {"rising": ("up", "📈"), "declining": ("down", "📉"), "stable": ("flat", "➖")}
        cards = []
        for sig in signals[:9]:
            kind, icon = cls.get(sig["direction"], ("flat", "•"))
            # the article names an area, not a percentage: show the area, keep the
            # original sentence only as the hover title (it is a quote, not our copy)
            evidence = sig["evidence"]
            area = _loc(sig, "area", lang)
            body = t["named_area"].format(area=area) if area else evidence
            cards.append(
                '<div class="tr-card ' + kind + '" title="' + evidence.replace('"', "'") + '">'
                + '<div class="tr-skill">' + skill_label(lang, sig["skill"]) + '</div>'
                + '<div class="tr-dir">' + icon + " " + t.get(sig["direction"], sig["direction"]) + '</div>'
                + '<span class="tr-badge" style="max-width:100%;white-space:normal;line-height:1.35;'
                  'font-size:10.5px;font-weight:500">' + body + '</span>'
                + '</div>'
            )
        st.markdown('<div class="tr-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)

    st.caption(t["proxy_caveat"])


def future_skill_panel(t: dict, lang: str) -> None:
    """Layer 3 — global employer forecasts, kept separate from local observations."""
    path = DATA / "trends" / "wef_future_jobs_2025.json"
    try:
        d = read_snapshot(path)
    except Exception:
        return

    st.markdown(f"### {t['future_skill_title']}")
    st.caption(
        f"**{t['future_skill_note']}** · {_loc(d, 'source', lang)} · "
        f"{d.get('published')} · {d.get('horizon')} · [{t['view_source']}]({d.get('source_url')})"
    )
    signals = d.get("skill_signals") or []
    if signals:
        st.markdown(TREND_CSS, unsafe_allow_html=True)
        cls = {"rising": ("up", "📈"), "declining": ("down", "📉"), "stable": ("flat", "➖")}
        cards = []
        for sig in signals:
            kind, icon = cls.get(sig["direction"], ("flat", "•"))
            name = _loc(sig, "skill", lang)
            evidence = _loc(sig, "evidence", lang)
            mapping = _loc(sig, "mapping_note", lang)
            body = evidence + (f" {mapping}" if mapping else "")
            known = {key for role in load_roles() for key in normalize_skills(role.required_skills)}
            mapping_kind = sig.get("mapping_kind") if sig.get("match_key") in known else "unmapped"
            mapping_label = (
                t["mapping_unmapped"] if mapping_kind == "unmapped"
                else t["mapping_proxy"] if mapping_kind == "proxy"
                else t["mapping_aligned"]
            )
            cards.append(
                '<div class="tr-card ' + kind + '" title="' + body.replace('"', "'") + '">'
                + '<div class="tr-skill">' + name + '</div>'
                + '<div class="tr-dir">' + icon + " " + t.get(sig["direction"], sig["direction"]) + '</div>'
                + '<div class="tr-evidence" style="font-size:10px;color:#6b765b;margin:3px 0">' + mapping_label + '</div>'
                + '<span class="tr-badge" style="max-width:100%;white-space:normal;line-height:1.35;'
                  'font-size:10.5px;font-weight:500">' + evidence + '</span>'
                + '</div>'
            )
        st.markdown('<div class="tr-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
    st.caption(t["future_skill_caveat"])


def team_trend_source_note(t: dict) -> None:
    """Keep HR and curriculum views explicit about the forecast behind scores."""
    path = DATA / "trends" / "wef_future_jobs_2025.json"
    try:
        source_url = json.loads(path.read_text(encoding="utf-8")).get("source_url")
    except Exception:
        source_url = None
    link = f' · [{t["view_source"]}]({source_url})' if source_url else ""
    st.caption(t["team_wef_note"] + link)


def trend_cards(t: dict, trend: dict, lang: str = "en") -> None:
    """Local job-offering counts, local named skills and global forecasts."""
    dosm_panel(t, lang)
    st.divider()
    skill_evidence_panel(t, lang)
    st.divider()
    future_skill_panel(t, lang)


def role_card(t: dict, result: dict, expanded: bool = False, lang: str = "en") -> None:
    c = result["components"]
    head = f"{result['score']:.1f} · {role_label(lang, result['role'])} · SDG {', '.join(result['sdg'])}"
    with st.expander(head, expanded=expanded):
        ui = copy_for(lang)
        st.markdown(
            score_panel(result["score"], [
                (ui["weighted"], c["coverage"]),
                (t["focus"], c.get("focus", 0)),
                (t["transfer"], c["transfer"]),
                (t["trend"], c["trend"]),
                (f'{t["gapcost"]} · {ui["lower"]}', c["gap_cost"]),
            ], lang),
            unsafe_allow_html=True,
        )
        close_items = []
        for x in result["missing"]:
            tier = result.get("tiers", {}).get(x)
            tag = f" ({t['tier_' + tier]})" if tier else ""
            close_items.append(skill_label(lang, x) + tag)
        close = ", ".join(close_items) or t["none"]
        total = len(result["covered"]) + len(result["missing"])
        pct = round(100 * len(result["covered"]) / total) if total else 0
        st.caption(t["why_score"].format(total, len(result["covered"]), pct))
        st.markdown(f"**{t['have']} ({len(result['covered'])})**")
        st.markdown(skill_chips([skill_label(lang, x) for x in result["covered"]]), unsafe_allow_html=True)
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
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
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
            if st.button(t["p1_btn"], type="primary", width="stretch"):
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
            if st.button(t["p2_btn"], type="primary", width="stretch"):
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
            if st.button(t["p3_btn"], type="primary", width="stretch"):
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

def clear_skill_draft() -> None:
    """Called before widgets render or as a callback; keep upload digest consumed."""
    st.session_state["skill_draft_labels"] = []
    st.session_state["skill_draft_dirty"] = False
    st.session_state["skill_query"] = ""
    st.session_state["skill_search_pick"] = []
    for group in TAXONOMY:
        st.session_state[f"ms_{group}"] = []


def clear_current_skills() -> None:
    clear_skill_draft()
    st.session_state["skills"] = []


def update_skill_draft(widget_key: str, visible_labels: list[str]) -> None:
    previous = set(st.session_state.get("skill_draft_labels", []))
    selected = set(st.session_state.get(widget_key, []))
    st.session_state["skill_draft_labels"] = sorted((previous - set(visible_labels)) | selected)
    st.session_state["skill_draft_dirty"] = True
    draft = st.session_state["skill_draft_labels"]
    for group, items in TAXONOMY.items():
        key = f"ms_{group}"
        if key != widget_key:
            st.session_state[key] = [x for x in draft if x in items]
    if widget_key != "skill_search_pick":
        sync_search_draft()


def sync_search_draft() -> None:
    lang = st.session_state.get("lang", "en")
    query = st.session_state.get("skill_query", "").strip().casefold()
    st.session_state["skill_search_pick"] = [
        x for x in st.session_state.get("skill_draft_labels", [])
        if query and query in (x + " " + skill_option_label(lang, x)).casefold()
    ]


def screen_js_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    step_banner(t)
    st.subheader(t["intake_h"])

    persona = st.radio(
        t["persona_q"], ["worker", "grad"], horizontal=True,
        format_func=lambda k: t["persona_worker"] if k == "worker" else t["persona_grad"],
    )
    st.session_state["persona"] = persona

    st.markdown(f'<div class="sr-pill">{t["persona_ctx"]}</div>', unsafe_allow_html=True)

    if persona == "worker":
        fields = ["all"] + list(FIELD_DOMAIN)
        chosen = st.selectbox(t["target_field"], fields,
            index=fields.index(st.session_state.get("worker_field", "all")) if st.session_state.get("worker_field", "all") in fields else 0,
            key="worker_field_widget",
            format_func=lambda f: t["all_fields"] if f == "all" else field_label(st.session_state.get("lang", "en"), f))
        st.session_state["worker_field"] = chosen
        c1, c2 = st.columns(2)
        with c1:
            st.session_state["years"] = st.number_input(
                t["q_years"], min_value=0, max_value=45, value=6, step=1,
                help=t["num_help"],
            )
            st.session_state["urgency"] = st.selectbox(
                t["q_urgency"], ["now", "6m", "12m"],
                format_func=lambda k: t["urg_" + k],
            )
        with c2:
            st.session_state["hours"] = st.number_input(
                t["q_hours"], min_value=1, max_value=40, value=8, step=1,
                help=t["num_help"],
            )
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
            _lang = st.session_state.get("lang", "en")
            remembered = st.session_state.get("graduate_field", st.session_state.get("field", "Business Administration"))
            group_names = list(FIELDS)
            remembered_group = next((g for g in group_names if remembered in FIELDS[g]), group_names[0])
            _group = st.selectbox(
                t["q_field"], group_names, index=group_names.index(remembered_group),
                format_func=lambda g: group_label(_lang, g),
            )
            st.session_state["graduate_field"] = st.selectbox(
                t["q_field_detail"], FIELDS[_group], label_visibility="visible",
                index=FIELDS[_group].index(remembered) if remembered in FIELDS[_group] else 0,
                format_func=lambda f: field_label(_lang, f),
            )
        with c2:
            st.session_state["intern"] = st.number_input(
                t["q_intern"], min_value=0, max_value=24, value=0, step=1,
                help=t["num_help"],
            )
            st.session_state["grad_year"] = st.selectbox(t["q_grad_year"], [2026, 2027, 2028])
        st.session_state["hours"] = st.slider(t["q_hours"], 1, 20, 10)
        st.caption(t["grad_note"])

    st.divider()
    st.markdown(f'<div class="sr-pill">{t["opt_a"]}</div>', unsafe_allow_html=True)
    up = st.file_uploader(t["uploader"], type=["txt", "md", "pdf"])
    if up is not None:
        # getvalue does not consume the upload stream on subsequent reruns.
        digest = hashlib.sha256(up.getvalue()).hexdigest()
        if digest != st.session_state.get("processed_upload_digest"):
            up.seek(0)
            found = normalize_skills(cv_to_skills(up))
            st.session_state["upload_parsed_skills"] = found
            st.session_state["processed_upload_digest"] = digest
            st.session_state["skills"] = list(found)
            clear_skill_draft()
            if found:
                st.success(t["detected"].format(len(found), ", ".join(found)))
            else:
                st.warning(t["not_detected"])
    st.caption(t["uploader_hint"])
    st.caption(t["upload_state_note"])

    st.markdown(f'<div class="sr-pill">{t["opt_b"]}</div>', unsafe_allow_html=True)
    lang = st.session_state.get("lang", "en")
    st.caption(copy_for(lang)["skills_note"])

    # A single searchable list across every category: type a word, pick the skill.
    _all_labels = [label for group_items in TAXONOMY.values() for label in group_items]
    _query = st.text_input(t["skill_search"], placeholder=t["skill_search_ph"], key="skill_query", on_change=sync_search_draft)
    if _query.strip():
        _hits = [x for x in _all_labels if _query.strip().casefold() in
                 (x + " " + skill_option_label(lang, x)).casefold()]
        if _hits:
            st.session_state.setdefault("skill_search_pick", [x for x in st.session_state.get("skill_draft_labels", []) if x in _hits])
            st.multiselect(
                t["skill_search_results"], options=_hits, key="skill_search_pick",
                on_change=update_skill_draft, args=("skill_search_pick", _hits),
                format_func=lambda x: skill_option_label(lang, x),
                placeholder=t["ms_placeholder"],
            )
        else:
            st.caption(t["skill_search_none"].format(_query))
    groups = list(TAXONOMY.items())
    for offset in range(0, len(groups), 2):
        columns = st.columns(2, gap="medium")
        for column, (group, items) in zip(columns, groups[offset:offset + 2]):
            with column:
                st.markdown(f"**{cat(lang, group)}**")
                widget_key = f"ms_{group}"
                st.session_state.setdefault(widget_key, [x for x in st.session_state.get("skill_draft_labels", []) if x in items])
                st.multiselect(
                    group, options=list(items), key=widget_key,
                    on_change=update_skill_draft, args=(widget_key, list(items)),
                    label_visibility="collapsed", placeholder=t["ms_placeholder"],
                    format_func=partial(skill_option_label, lang),
                )
    st.caption(t["draft_note"])
    if st.button(t["use_skills"], width="stretch", disabled=not st.session_state.get("skill_draft_dirty", False)):
        st.session_state["skills"] = normalize_skills([
            skill for label in st.session_state.get("skill_draft_labels", []) for skill in LABEL_TO_KEYS[label]
        ])
        st.session_state["skill_draft_dirty"] = False
    st.button(t["clear_skills"], width="stretch", on_click=clear_current_skills)

    current = st.session_state.get("skills") or []
    if current:
        st.markdown(f"**{t['current']} · {len(set(current))}**")
        st.markdown(
            skill_chips([skill_label(lang, x) for x in sorted(set(current))]),
            unsafe_allow_html=True,
        )
        if len(set(current)) > 10:
            st.caption(t["too_many"])

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button(t["back"], width="stretch"):
            reset()
    with c2:
        if not current:
            st.caption(t["empty_skills"])
        if st.button(t["continue"], type="primary", width="stretch", disabled=not current):
            go("js_results")


# --------------------------------------------------------------------------- #
# Screen: jobseeker results — persona aware
# --------------------------------------------------------------------------- #

def _evidence_lines(t: dict, lang: str, role: Role | None, trend: dict) -> list[str]:
    """One plain sentence per signal: what the source says, and what it cannot say."""
    wanted = set(normalize_skills(role.required_skills)) if role else set()
    hits = [s for s in (trend.get("signals") or []) if signal_key(s) in wanted]
    hits.sort(key=lambda s: -abs(_signal_strength(s)))
    period = trend.get("latest_period") or ""
    prev_period = trend.get("previous_period") or ""
    forecast = bool(trend.get("forecast"))
    out = []
    for s in hits[:2]:
        occ = _loc(s, "occupation", lang)
        if occ and s.get("offers") is not None:
            # observed Malaysian counts: give the two numbers and the change
            out.append(t["ev_line"].format(
                occ=occ,
                cur=f'{s["offers"]:,}',
                prev=f'{s.get("offers_prev") or 0:,}',
                period=period,
                prev_period=prev_period,
                chg=f'{s.get("change_pct") or 0:+.1f}%',
            ))
        else:
            # named-skill or forecast signal: name the area in plain words
            area = (_loc(s, "area", lang) or s.get("quote_area")
                    or skill_plain(lang, s["skill"]))
            out.append(t["evidence_forecast"].format(area=area) if forecast
                       else t["evidence_named"].format(area=area))
    return out


def why_block(t: dict, lang: str, result: dict, role: Role | None, trend: dict,
              skills: list[str], hours: int) -> None:
    """Three plain-language reasons for the top match: transfer, gap, evidence.

    Reads existing model fields only — no new score, no new number invented here.
    When there is no gap the three columns would be empty boxes, so it degrades to
    one line plus the evidence instead of showing "none / nothing missing".
    """
    missing = result["missing"]
    lines = _evidence_lines(t, lang, role, trend)

    if not missing:
        st.caption(t["why_gap_none"])
        for line in lines[:2]:
            st.caption(line)
        return

    st.markdown(f"**{t['why_title']}**")
    left, mid, right = st.columns(3)

    with left:
        pairs = []
        for gap in missing:
            best = max(((p, TRANSFERABILITY.get((p, gap), 0.0)) for p in skills),
                       key=lambda kv: kv[1], default=(None, 0.0))
            if best[0] and best[1] >= 0.4:
                pairs.append((best[1], best[0], gap))
        pairs.sort(reverse=True)
        st.markdown(f"**{t['why_transfer']}**")
        if pairs:
            for score, have, gap in pairs[:3]:
                st.caption(t["why_transfer_item"].format(
                    a=skill_plain(lang, have), b=skill_plain(lang, gap), pct=round(score * 100)))
        else:
            st.caption(t["why_transfer_none"])

    with mid:
        st.markdown(f"**{t['why_gap']}**")
        core = sum(1 for s in missing if role and role.tier_of(s) == "core")
        weeks = sum(learning_duration(s, load_courses(), hours)["weeks"] for s in missing)
        st.caption(t["path_note"].format(hours))
        st.caption(t["why_gap_body"].format(
            n=len(missing), total=len(missing) + len(result["covered"]),
            core=t["core_phrase"].format(k=core) if core else "",
            weeks=weeks, hours=hours))

    with right:
        st.markdown(f"**{t['why_trend']}**")
        if lines:
            for line in lines:
                st.caption(line)
        else:
            st.caption(t["why_trend_none"])


def screen_js_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    step_banner(t)
    skills = st.session_state.get("skills") or []
    persona = st.session_state.get("persona", "worker")
    if not skills:
        st.warning(t["not_detected"])
        if st.button(t["back"]):
            go("js_intake")
        return

    base_roles = load_roles()
    hours = st.session_state.get("hours", 8)

    # Domain-aware filtering: never recommend a role from an unrelated field.
    field = st.session_state.get("worker_field", "all") if persona == "worker" else st.session_state.get("graduate_field", st.session_state.get("field", "Business Administration"))
    raw_profile = st.session_state.get("skills") or skills
    # keep only skills the catalogue knows about (drop anything typed via an old key)
    known = {sk for r in base_roles for sk in r.required_skills}
    skills = [sk for sk in raw_profile if sk in known] or raw_profile
    same, adjacent = roles_for_field(base_roles, field)
    pool_base = filter_roles(base_roles, ROLE_META, persona, field, FIELD_DOMAIN, ADJACENT)

    st.subheader(t["p1"])
    st.markdown(
        skill_chips([skill_label(st.session_state.get("lang", "en"), x) for x in sorted(set(skills))]),
        unsafe_allow_html=True,
    )
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

    # Section 2 stays open: the DOSM counts and named-skill evidence are
    # the proof behind every recommendation, so they must be visible without a click.
    lang_now = st.session_state.get("lang", "en")
    st.caption(copy_for(lang_now)["market_note"])
    st.subheader(t["p2"])

    # The ranking source is a user-visible choice, so "we track the market" is
    # something the judge can switch and see, not a claim on a slide.
    src = st.radio(
        t["src_label"],
        ["jobstreet", "wef"],
        horizontal=True,
        key="trend_source",
        format_func=lambda k: t["src_" + k],
    )
    trend = load_snapshot(src)
    st.markdown(
        "<style>.src-badge{display:inline-block;padding:2px 9px;border-radius:999px;"
        "font-size:10.5px;font-weight:700;letter-spacing:.06em;vertical-align:middle;"
        "background:#e4eed6;color:#3f5a1e}</style>"
        f'<div style="margin:2px 0 6px"><span class="src-badge">{t["src_badge_forecast"] if trend.get("forecast") else t["src_badge_obs"]}</span> '
        f'<span style="font-size:11.5px;color:#7a836a">{_loc(trend, "source", lang_now)}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(t["src_note_" + src])
    trend_cards(t, trend, lang_now)
    roles = apply_trend(pool_base, trend)

    st.subheader(t["p3"])
    scenario = st.radio(
        t["scenario"], ["moderate", "fast"], horizontal=True,
        format_func=lambda x: t["moderate"] if x == "moderate" else t["fast"],
    )
    results = rank(skills, roles, scenario=scenario)

    # ---- does the recommendation survive a different evidence source? ----
    # Same profile and model, viewed through a Malaysian article and a global
    # employer forecast. The comparison exposes source sensitivity.
    def _under(kind: str) -> dict[str, tuple[int, float]]:
        ranked = rank(skills, apply_trend(pool_base, load_snapshot(kind)), scenario=scenario)
        return {r["role"]: (i + 1, r["score"]) for i, r in enumerate(ranked)}

    _u_jobstreet, _u_wef = _under("jobstreet"), _under("wef")
    with st.expander(t["robust_title"], expanded=True):
        rows = []
        for r in results[:5]:
            (pa, sa) = _u_jobstreet.get(r["role"], (0, 0.0))
            (pb, sb) = _u_wef.get(r["role"], (0, 0.0))
            rows.append({
                t["col_role"]: role_label(lang_now, r["role"]),
                t["robust_jobstreet"]: pa,
                t["robust_wef"]: pb,
                t["robust_score_jobstreet"]: sa,
                t["robust_score_wef"]: sb,
                t["robust_delta"]: round(sb - sa, 1),
                t["robust_verdict"]: t["robust_hold"] if pa <= 5 and pb <= 5 else t["robust_sensitive"],
            })
        st.dataframe(rows, width="stretch", hide_index=True)
        st.caption(t["robust_note"])

    # ---- uncertainty: show both scenarios side by side, ranked side by side ----
    _fast = rank(skills, roles, scenario="fast")
    _mod = results if scenario == "moderate" else rank(skills, roles, scenario="moderate")
    _pos_mod = {r["role"]: i + 1 for i, r in enumerate(_mod)}
    _pos_fast = {r["role"]: i + 1 for i, r in enumerate(_fast)}
    _score_fast = {r["role"]: r["score"] for r in _fast}
    with st.expander(t["scen_compare"], expanded=False):
        st.markdown(
            '<span style="display:inline-block;padding:2px 9px;border-radius:999px;font-size:10.5px;'
            'font-weight:700;letter-spacing:.06em;background:#f7e6c8;color:#7a4d0a">'
            f'{t["src_badge_scenario"]}</span>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            [
                {
                    t["col_role"]: role_label(st.session_state.get("lang", "en"), r["role"]),
                    t["col_mod"]: r["score"],
                    t["col_fast"]: _score_fast.get(r["role"], 0),
                    t["col_delta"]: round(_score_fast.get(r["role"], 0) - r["score"], 1),
                    t["col_pos"]: f'#{_pos_mod[r["role"]]} -> #{_pos_fast.get(r["role"], 0)}',
                }
                for r in _mod[:5]
            ],
            width="stretch",
            hide_index=True,
        )
        st.caption(t["scen_note"])
        st.caption(t["both_top"].format(
            a=role_label(lang_now, _mod[0]["role"]), b=role_label(lang_now, _fast[0]["role"])))
        gap_both = set(_mod[0]["missing"]) & set(_fast[0]["missing"])
        st.markdown(f"**{t['both_title']}**")
        if gap_both:
            st.markdown(
                skill_chips([skill_label(lang_now, x) for x in sorted(gap_both)]),
                unsafe_allow_html=True,
            )
            st.caption(t["both_note"])
        else:
            st.caption(t["both_none"])

    # ---- neutral summary driven by weighted coverage, not by a gap count ----
    top1 = results[0]
    cover = top1["components"]["coverage"]
    missing_n = len(top1["missing"])
    total_n = len(top1["covered"]) + missing_n
    top_role = role_plain(lang_now, top1["role"])
    missing_labels = ", ".join(skill_plain(lang_now, x) for x in top1["missing"]) or t["none"]

    if missing_n == 0:
        st.success(t["summary_full"].format(top_role, round(cover * 100)))
    elif cover >= 0.7:
        st.success(t["summary_strong"].format(top_role, round(cover * 100), missing_labels))
    elif cover >= 0.4:
        st.info(t["summary_partial"].format(top_role, round(cover * 100), missing_n, missing_labels))
    else:
        st.warning(t["summary_weak"].format(top_role, round(cover * 100), missing_n, total_n))

    # the persona advice and the field note are already visible above; one short
    # line here says how wide the shortlist is, and nothing else
    if persona == "worker":
        # Report the explicit worker scope; never infer it from graduate state.
        _scope = t["all_fields"] if field == "all" else t["target_field"] + ": " + field_label(lang_now, field)
    elif same:
        _scope = t["domain_same"].format(field_label(lang_now, field), len(same))
    else:
        _scope = t["domain_adjacent"].format(field_label(lang_now, field))
    st.caption(_scope)
    roles_by_name = {x.name: x for x in roles}
    why_block(t, lang_now, top1, roles_by_name.get(top1["role"]), trend, skills, hours)
    for i, r in enumerate(results[:4]):
        r["tiers"] = {sk: roles_by_name.get(r["role"], Role(r["role"], [], 0)).tier_of(sk) for sk in r["missing"]}
        role_card(t, r, expanded=(i == 0), lang=lang_now)

    st.caption(t["coverage_disclaimer"])
    st.subheader(t["p4"])
    top = results[0]
    courses = load_courses()
    if top["missing"]:
        total_required = len(top["covered"]) + len(top["missing"])
        plan = pathway(top)
        # Cheapest-first is the base order; the chosen evidence source then pulls the
        # skills the market currently rewards towards the front of the queue.
        _evidence = {signal_key(s): _signal_strength(s) for s in (trend.get("signals") or []) if signal_key(s) is not None}
        plan.sort(key=lambda p_: GAP_COST.get(p_["skill"], 0.7) - 0.35 * _evidence.get(p_["skill"], 0.0))
        for _i, _p in enumerate(plan, 1):
            _p["step"] = _i
        # Product metrics, computed from this profile — never an outcome claim.
        prof_full = skills + [p_["skill"] for p_ in plan]
        after_score = rank(prof_full, roles, scenario=scenario)[0]["score"]
        total_weeks = sum(learning_duration(p_["skill"], courses, hours)["weeks"] for p_ in plan)
        m1, m2, m3 = st.columns(3)
        m1.metric(t["impact_gap"], len(top["missing"]))
        m2.metric(t["impact_weeks"], total_weeks)
        m3.metric(t["impact_roles"], after_score,
                  delta=round(after_score - top["score"], 1), delta_color="normal")
        st.caption(t["impact_note"])
        st.write(t["gap"].format(role_plain(lang_now, top["role"]), len(top["missing"]), total_required))
        step_rows, course_rows = [], []
        for p_ in plan:
            weeks = learning_duration(p_["skill"], courses, hours)["weeks"]
            step_rows.append({
                t["step"]: p_["step"],
                t["skill"]: skill_label(lang_now, p_["skill"]),
                t["weeks"]: weeks,
                t["duration_basis"]: t[learning_duration(p_["skill"], courses, hours)["basis"]],
            })
            c = courses.get(p_["skill"])
            if c:
                course_rows.append({
                    t["col_course"]: c["title"],
                    t["col_provider"]: c["provider"],
                    t["col_hours"]: c["hours"],
                    t["col_cost"]: c["cost"],
                    t["col_link"]: c["url"],
                })
        st.markdown(
            learning_path([
                (row[t["step"]], row[t["skill"]], row[t["weeks"]]) for row in step_rows
            ], lang_now),
            unsafe_allow_html=True,
        )
        st.caption(f"{t['path_note'].format(hours)} {t['path_evidence'].format(src=t['src_' + src])}")

        # The pathway is a plan only if the ranking actually moves. Re-score the
        # user's own profile after each step and show it.
        st.markdown(f"**{t['bridge_title']}**")
        bridge, prof = [], list(skills)
        for p_ in plan:
            prof = prof + [p_["skill"]]
            best = rank(prof, roles, scenario=scenario)[0]
            bridge.append({
                t["bridge_step"]: f'{p_["step"]}. {skill_label(lang_now, p_["skill"])}',
                t["bridge_weeks"]: learning_duration(p_["skill"], courses, hours)["weeks"],
                t["bridge_best"]: role_label(lang_now, best["role"]),
                t["bridge_score"]: best["score"],
            })
        st.dataframe(bridge, width="stretch", hide_index=True)
        st.caption(t["bridge_note"])

        st.dataframe(step_rows, hide_index=True, width="stretch")
        no_course = [p_["skill"] for p_ in plan if p_["skill"] not in courses]
        if no_course:
            st.caption(t["no_course"] + ": " + ", ".join(skill_label(lang_now, x) for x in no_course))
        if course_rows:
            st.markdown(f"**{t['courses_title']}**")
            st.dataframe(
                course_rows,
                width="stretch",
                hide_index=True,
                column_config={t["col_link"]: st.column_config.LinkColumn(t["col_link"])},
            )
            st.caption(t["courses_note"])
        else:
            # No verified course for these skills: give a search route instead of
            # pretending a resource exists.
            st.caption(t["search_caption"].format(
                ", ".join(skill_label(lang_now, x) for x in top["missing"])))
            links = []
            for x in top["missing"]:
                if x in courses:
                    continue
                query = quote_plus(x)
                links.append(f"[{t['course_search_link']} · {skill_plain(lang_now, x)}]"
                             f"(https://www.coursera.org/search?query={query})")
            if links:
                st.markdown(" · ".join(links))
    else:
        st.success(t["covered_all"])

    with st.expander(t["disclose_title"]):
        st.markdown(t["disclose_body"])
        st.markdown(t["disclose_extra"])

    # ---- 5. SDG contribution -------------------------------------------------
    # The heading keeps its left rule. The toggle is a normal Streamlit button with a
    # plain label: no CSS overrides, no anchors, no overlays, so it always clicks.
    q_open = st.session_state.get("show_sdg_wheel", False)
    st.markdown(
        '<div class="sdg-head-row">'
        f'<span class="sdg-head-text">{t["p5"]}</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        ("▾ " if q_open else "▸ ") + t["sdg_open_btn"],
        key="sdg_toggle_btn",
        help=t["sdg_help_tip"],
    ):
        st.session_state["show_sdg_wheel"] = not q_open
        q_open = not q_open

    summary = sdg_summary(results[:4])
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in summary.items()) or "—")

    # quick colour chips for the goals in play
    chips = []
    for goal, count in summary.items():
        colour = SDG_COLOURS.get(int(goal.split(".")[0]), "#888888")
        chips.append(
            f'<span style="display:inline-block;background:{colour};color:#fff;'
            f'padding:3px 10px;border-radius:999px;font-size:12px;margin:0 6px 6px 0">'
            f'SDG {goal} · {count}</span>'
        )
    if chips:
        st.markdown("".join(chips), unsafe_allow_html=True)

    # Skill level: which targets the skills on this pathway actually serve.
    skill_sdg = load_skill_sdg()
    step_skills = [p["skill"] for p in pathway(top)] if top["missing"] else list(top["covered"][:3])
    mapped = [(s_, skill_sdg[s_]) for s_ in step_skills if s_ in skill_sdg]
    if mapped:
        st.markdown(f"**{t['skill_sdg_title']}**")
        rows = "".join(
            f'<span style="display:inline-block;background:#eef3e6;color:#3f4a26;'
            f'padding:3px 10px;border-radius:999px;font-size:12px;margin:0 6px 6px 0">'
            f'{skill_plain(lang_now, s_)} · {" / ".join(info["targets"])}</span>'
            for s_, info in mapped
        )
        st.markdown(rows, unsafe_allow_html=True)
        reached = sorted({t_ for _, info in mapped for t_ in info["targets"]})
        st.caption(t["skill_sdg_note"].format(n=len(mapped), targets=", ".join(reached)))

    st.caption(t["sdg_note"])

    if st.session_state.get("show_sdg_wheel", False):
        wheel = ROOT / "docs" / f"sdg_wheel_{lang_now}.png"
        if not wheel.exists():
            wheel = ROOT / "docs" / "sdg_wheel_en.png"
        if wheel.exists():
            left, mid, right = st.columns([1, 6, 1])
            with mid:
                st.image(str(wheel), caption=t["sdg_wheel_caption"], width="stretch")
        else:
            st.info(t["sdg_wheel_caption"])



# --------------------------------------------------------------------------- #
# Screen: HR intake / results
# --------------------------------------------------------------------------- #

def screen_hr_intake() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    step_banner(t)
    st.subheader(t["hr_h"])
    team_trend_source_note(t)
    st.caption(t["hr_sub"])

    roster: dict[str, int] = {}
    for r in load_roles():
        n = st.slider(r.name, 0, 20, 1 if r.name.startswith("AI Operations") else 0)
        if n:
            roster[r.name] = n

    st.caption(t["hr_tip"])
    if st.button(t["analyse"], type="primary", width="stretch", disabled=not roster):
        st.session_state["roster"] = roster
        go("hr_results")
    if st.button(t["back"]):
        reset()


def screen_hr_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    step_banner(t)
    roster: dict[str, int] = st.session_state.get("roster") or {}
    if not roster:
        st.warning(t["hr_h"])
        if st.button(t["back"]):
            go("hr_intake")
        return

    roles = {r.name: r for r in apply_trend(load_roles(), load_snapshot("wef"))}
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
        width="stretch", hide_index=True,
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
    step_banner(t)
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
    _lang_cc = st.session_state.get("lang", "en")
    targets = st.multiselect(
        t["cc_targets"], options=[r.name for r in roles],
        default=[r.name for r in roles[:2]],
        format_func=lambda n: role_label(_lang_cc, n),
    )
    st.session_state["targets"] = targets

    if targets:
        needed = sorted({s for r in roles if r.name in targets for s in r.required_skills})
        taught = st.multiselect(
            t["cc_taught"], options=needed, default=needed[:2],
            format_func=lambda x: skill_label(_lang_cc, x),
        )
        st.session_state["taught"] = taught

        if st.button(t["cc_run"], type="primary", width="stretch"):
            go("cc_results")

    if st.button(t["back"]):
        reset()


def screen_cc_results() -> None:
    t = T(st.session_state.get("lang", "en"))
    screen_wrap()
    top_bar(t)
    step_banner(t)
    targets = st.session_state.get("targets") or []
    taught = st.session_state.get("taught") or []
    if not targets:
        st.warning(t["cc_h"])
        if st.button(t["back"]):
            go("cc_intake")
        return

    roles = {r.name: r for r in apply_trend(load_roles(), load_snapshot("wef"))}
    needed = sorted({s for r in roles.values() if r.name in targets for s in r.required_skills})
    covered = [s for s in needed if s in taught]
    missing = [s for s in needed if s not in taught]
    coverage = len(covered) / len(needed) if needed else 0

    st.subheader(t["cc_overview"])
    team_trend_source_note(t)
    a, b, c = st.columns(3)
    a.metric(t["cc_prog_lbl"], st.session_state.get("prog", "—"))
    b.metric(t["cc_cohort_lbl"], st.session_state.get("cohort", 0))
    c.metric(t["coverage"], f"{coverage * 100:.0f}%")

    st.subheader(t["cc_curriculum"])
    st.caption(t["cc_curriculum_note"].format(len(covered), len(needed)))
    st.dataframe(
        [{t["col_skill"]: s, t["cc_status"]: t["cc_have"] if s in covered else t["cc_miss"]}
         for s in needed],
        width="stretch", hide_index=True,
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
        width="stretch", hide_index=True,
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
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

try:
    STAGES.get(STAGE, screen_landing)()
except Exception as exc:
    st.error(_T["error"])
    st.caption(f"{type(exc).__name__}: {exc}")
    if st.button(_T["back_start"]):
        reset()
