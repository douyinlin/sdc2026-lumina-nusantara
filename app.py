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

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from utils import Role, pathway, rank, sdg_summary  # noqa: E402

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
  70%  { opacity: 1; }
  100% { opacity: 0; visibility: hidden; }
}
@keyframes sr-mark {
  0%   { transform: scale(0.7); opacity: 0; letter-spacing: -2px; }
  55%  { transform: scale(1.06); opacity: 1; letter-spacing: 2px; }
  100% { transform: scale(1); opacity: 1; letter-spacing: 4px; }
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
  position: fixed; inset: 0; z-index: 999999;
  display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 50% 42%, #f7faf3 0%, #eef3e6 45%, #e3ebd8 100%);
  animation: sr-curtain 1s ease forwards;
  pointer-events: none;
}
.sr-mark {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 34px; font-weight: 700; color: #6f7f42;
  animation: sr-mark 0.9s cubic-bezier(.2,.8,.25,1) forwards;
}
.sr-bar {
  position: absolute; bottom: 0; left: 0; height: 3px; width: 100%;
  background: linear-gradient(90deg, transparent, #8A9A5B, transparent);
  animation: sr-sweep 1s ease forwards;
}
.sr-enter { animation: sr-rise 0.55s ease-out both; }
</style>
"""

INTRO_HTML = """
<div class="sr-curtain">
  <div class="sr-mark">📡 SKILLRADAR</div>
  <div class="sr-bar"></div>
</div>
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


def screen_wrap() -> None:
    """Fade content in when arriving from a transition."""
    if st.session_state.pop("entering", False):
        st.markdown(ANIM_CSS, unsafe_allow_html=True)
        st.markdown('<div class="sr-enter">', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def go(stage: str) -> None:
    transition_into(stage)


def reset() -> None:
    for k in list(st.session_state):
        if k != "lang":
            del st.session_state[k]
    st.session_state["stage"] = "landing"
    st.rerun()


def top_bar() -> None:
    left, mid, right = st.columns([1, 2, 1])
    with left:
        st.markdown("### 📡 SkillRadar MY")
    with right:
        if st.button("🔄 Re-evaluate", use_container_width=True,
                     help="Clear everything and start a new assessment"):
            reset()


def trend_cards(trend: dict) -> None:
    source = trend.get("source_url")
    retrieved = trend.get("retrieved_at")
    label = "Simulated data (not real market evidence)" if trend.get("is_simulated") else "Public source"
    st.caption(f"**{label}** · source: {source or '—'} · retrieved: {retrieved or '—'}")
    signals = trend.get("signals") or []
    if not signals:
        st.info("No trend signals loaded.")
        return
    cols = st.columns(min(3, len(signals)))
    icon = {"rising": "📈", "declining": "📉", "stable": "➖"}
    for i, s in enumerate(signals[:6]):
        with cols[i % len(cols)]:
            st.metric(f"{icon.get(s['direction'], '•')} {s['skill']}",
                      s["direction"].title(), f"weight {s['weight']:+.1f}")


def role_card(result: dict, expanded: bool = False) -> None:
    c = result["components"]
    head = f"{result['score']:.1f} · {result['role']} · SDG {', '.join(result['sdg'])}"
    with st.expander(head, expanded=expanded):
        st.progress(min(1.0, result["score"] / 100))
        a, b, c1, d = st.columns(4)
        a.metric("Skill coverage", f"{c['coverage'] * 100:.0f}%")
        b.metric("Transferability", f"{c['transfer'] * 100:.0f}%")
        c1.metric("Demand trend", f"{c['trend'] * 100:.0f}%")
        d.metric("Gap cost", f"{c['gap_cost'] * 100:.0f}%")
        st.write(f"**Already have ({len(result['covered'])}):** {', '.join(result['covered']) or '—'}")
        st.write(f"**To close ({len(result['missing'])}):** {', '.join(result['missing']) or 'none'}")
        st.caption("Prototype estimate — the score is a weighted rule, not a hiring probability.")


# --------------------------------------------------------------------------- #
# Screen: landing
# --------------------------------------------------------------------------- #

def screen_landing() -> None:
    screen_wrap()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center'>📡 SkillRadar MY</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#666'>SDC 2026 · Domain 1 — see what skills are rising, "
        "which future roles fit you, and the fastest route to close the gap.<br>"
        "Every forecast shows its source and date. Predictions are estimates, not facts.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown("## 👤 I'm a jobseeker")
            st.write("Understand your skill gap, get matched future roles, and a step-by-step "
                     "reskilling plan mapped to the UN SDGs.")
            if st.button("Start as jobseeker →", type="primary", use_container_width=True):
                go("js_intake")
    with right:
        with st.container(border=True):
            st.markdown("## 🏢 I'm an HR / L&D manager")
            st.write("See your team's skills coverage against future roles, where the biggest "
                     "gaps are, and what to train first.")
            if st.button("Start as HR →", type="primary", use_container_width=True):
                go("hr_intake")

    st.markdown("---")
    st.caption("Demo uses synthetic profiles and public/simulated trend weights only — no real CVs, "
               "no personal data stored.")


# --------------------------------------------------------------------------- #
# Screen: jobseeker intake (full width)
# --------------------------------------------------------------------------- #

def screen_js_intake() -> None:
    screen_wrap()
    top_bar()
    st.subheader("Tell us about yourself")
    st.caption("Upload a CV or tick the skills you already have — you can edit the result either way.")

    tab_cv, tab_form = st.tabs(["📄 Upload a CV", "✅ Fill the questionnaire"])

    with tab_cv:
        up = st.file_uploader("Drop a CV here (synthetic files only)", type=["txt", "md", "pdf"])
        if up is not None:
            found = cv_to_skills(up)
            st.session_state["skills"] = found
            if found:
                st.success(f"Detected {len(found)} skill(s): {', '.join(found)}")
            else:
                st.warning("No known skill detected — use the questionnaire tab instead.")
        st.caption("No CV handy? Try `data/sample_cv.txt` from the repository.")

    with tab_form:
        picked: list[str] = []
        for group, items in TAXONOMY.items():
            st.markdown(f"**{group}**")
            labels = st.multiselect(
                f"{group} skills", options=list(items), key=f"ms_{group}",
                label_visibility="collapsed", placeholder="Select skills in this category…",
            )
            for label in labels:
                picked += LABEL_TO_KEYS[label]
            st.markdown("")
        if st.button("Use these skills", use_container_width=True):
            st.session_state["skills"] = picked

    current = st.session_state.get("skills") or []
    if current:
        st.info(f"**Current profile:** {', '.join(sorted(set(current)))}  ({len(set(current))} skills)")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("← Back", use_container_width=True):
            reset()
    with c2:
        if st.button("See my future-role matches →", type="primary", use_container_width=True,
                     disabled=not current):
            go("js_results")


# --------------------------------------------------------------------------- #
# Screen: jobseeker results
# --------------------------------------------------------------------------- #

def screen_js_results() -> None:
    screen_wrap()
    top_bar()
    skills = st.session_state.get("skills") or []
    if not skills:
        st.warning("No skills selected yet.")
        if st.button("← Back to intake"):
            go("js_intake")
        return

    trend = load_trend()
    roles = apply_trend(load_roles(), trend)

    st.subheader("1 · Your profile")
    st.write(", ".join(sorted(set(skills))))

    st.subheader("2 · Future skills radar")
    trend_cards(trend)

    st.subheader("3 · Best-fit future roles")
    scenario = st.radio("AI disruption scenario", ["moderate", "fast"], horizontal=True,
                        format_func=lambda x: "Moderate disruption" if x == "moderate" else "Fast disruption")
    results = rank(skills, roles, scenario=scenario)
    st.caption("Ranked by an explainable weighted score. Open a role to see the four components.")
    for i, r in enumerate(results[:4]):
        role_card(r, expanded=(i == 0))

    st.subheader("4 · Skills to close and your pathway")
    top = results[0]
    if top["missing"]:
        st.write(f"Gap for **{top['role']}**: {len(top['missing'])} of {len(top['required_skills'])} "
                 f"required skills missing.")
        st.table(pathway(top))
        st.caption("⚠️ Week estimates are indicative only, and resource links are a suggested search "
                   "direction on the HRD Corp directory — not a verified course price or duration.")
    else:
        st.success("You cover every skill for this role — look at the next option in the ranking.")

    st.subheader("5 · SDG contribution of this path")
    summary = sdg_summary(results[:4])
    st.write(", ".join(f"**SDG {k}** ({v})" for k, v in summary.items()) or "—")
    st.caption("SDG 4.4 relevant skills for employment · 8.5 full and productive employment · "
               "9.1 infrastructure and innovation · 8.2 productivity through innovation")

    st.subheader("6 · Scenario comparison")
    st.dataframe(
        [{"Role": m["role"], "Moderate": m["score"], "Fast": f["score"], "Δ": round(f["score"] - m["score"], 1)}
         for m, f in zip(rank(skills, roles, "moderate"), rank(skills, roles, "fast"))],
        use_container_width=True, hide_index=True,
    )
    st.caption("Same profile, two disruption speeds. Predictions are estimates, not facts.")


# --------------------------------------------------------------------------- #
# Screen: HR intake
# --------------------------------------------------------------------------- #

def screen_hr_intake() -> None:
    screen_wrap()
    top_bar()
    st.subheader("Describe your team")
    st.caption("Pick the roles in your team and how many people sit in each. We aggregate the skill "
               "requirement and show where the workforce coverage is weakest.")

    roles = load_roles()
    roster: dict[str, int] = {}
    for r in roles:
        n = st.slider(r.name, 0, 20, 1 if r.name.startswith("AI Operations") else 0)
        if n:
            roster[r.name] = n

    st.caption("Tip: keep 2–4 roles for a readable heatmap.")
    if st.button("Analyse workforce →", type="primary", use_container_width=True, disabled=not roster):
        st.session_state["roster"] = roster
        go("hr_results")

    if st.button("← Back"):
        reset()


# --------------------------------------------------------------------------- #
# Screen: HR results
# --------------------------------------------------------------------------- #

def screen_hr_results() -> None:
    screen_wrap()
    top_bar()
    roster: dict[str, int] = st.session_state.get("roster") or {}
    if not roster:
        st.warning("No team defined.")
        if st.button("← Back"):
            go("hr_intake")
        return

    trend = load_trend()
    roles = {r.name: r for r in apply_trend(load_roles(), trend)}
    total_people = sum(roster.values())

    st.subheader("Workforce overview")
    a, b, c = st.columns(3)
    a.metric("People in scope", total_people)
    b.metric("Roles tracked", len(roster))
    demand: dict[str, int] = {}
    for name, n in roster.items():
        for s in roles[name].required_skills:
            demand[s] = demand.get(s, 0) + n
    c.metric("Distinct skills required", len(demand))

    st.subheader("Priority skills to build")
    st.caption("Ranked by how many people across your team need the skill.")
    rows = [{"Skill": s, "People needing it": n, "Share of workforce": f"{n / max(total_people, 1) * 100:.0f}%"}
            for s, n in sorted(demand.items(), key=lambda kv: -kv[1])]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("Role-level view")
    for name, n in roster.items():
        role = roles[name]
        with st.expander(f"{name} · {n} people · SDG {', '.join(role.sdg)}"):
            st.write(f"**Required skills:** {', '.join(role.required_skills)}")
            st.write(f"**Market trend signal:** {'rising' if role.trend > 0.3 else 'declining' if role.trend < -0.2 else 'stable'}")
            st.caption("Aggregate demand — individual-level coverage is collected per employee in Phase 2.")

    st.subheader("Suggested reskilling plan")
    plan = []
    for i, (s, n) in enumerate(sorted(demand.items(), key=lambda kv: -kv[1])[:5], start=1):
        plan.append({"Priority": i, "Skill": s, "People": n,
                     "Suggested route": f"HRD Corp directory search: {s}"})
    st.table(plan)
    st.caption("⚠️ Suggested search directions, not verified courses. Confirm price, duration and "
               "HRD Corp claimability before committing budget.")

    st.subheader("SDG alignment of this team")
    sdg: dict[str, int] = {}
    for name in roster:
        for tag in roles[name].sdg:
            sdg[tag] = sdg.get(tag, 0) + 1
    st.write(", ".join(f"**SDG {k}** ({v} roles)" for k, v in sorted(sdg.items(), key=lambda kv: -kv[1])))

    st.caption("Synthetic demo data only — no employee records are collected or stored.")


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="SkillRadar MY", page_icon="📡", layout="wide")
st.session_state.setdefault("stage", "landing")

play_intro()

STAGES = {
    "landing": screen_landing,
    "js_intake": screen_js_intake,
    "js_results": screen_js_results,
    "hr_intake": screen_hr_intake,
    "hr_results": screen_hr_results,
}

STAGES.get(st.session_state["stage"], screen_landing)()
