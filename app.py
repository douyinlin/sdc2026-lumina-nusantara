"""SkillRadar MY — Streamlit application.

One-click start:  python app.py   (installs Streamlit automatically if missing)
Streamlit way   :  streamlit run app.py

The matching / pathway / SDG engine lives in ``src/utils.py``; this file only
handles screens and rendering so the engine stays unit-testable.

The bootstrap block below is deliberate: on a fresh Replit (or any fresh
machine) ``streamlit`` may not be installed yet, so instead of crashing with
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
# i18n — English / Bahasa Malaysia / 中文
# (Domain 1 good-to-have: multi-language support)
# --------------------------------------------------------------------------- #

I18N: dict[str, dict[str, str]] = {
    "English": {
        "tagline": "Lumina Nusantara · SDC 2026 · Domain 1 — every forecast carries its source and retrieval date; every role maps to the SDGs.",
        "who": "1 · Who are you today?",
        "how": "How would you like to tell us about yourself?",
        "mode_upload": "Upload a CV (PDF / TXT)",
        "mode_form": "Fill a short questionnaire",
        "how_help": "Domain 1 rule: use synthetic documents only — never upload a real CV.",
        "drop_cv": "Drop a CV here (synthetic only)",
        "cv_help": "PDF text is extracted automatically. Nothing is stored or sent anywhere.",
        "detected": "Detected {} skill(s): {}",
        "not_detected": "No known skill was detected. Try the questionnaire, or add the skill names to the CV text (we match against a fixed skill vocabulary).",
        "no_cv": "No CV handy? Use one of the sample profiles below.",
        "start_profile": "Start from a profile",
        "custom": "Custom",
        "skills_edit": "Your current skills (editable)",
        "scenario_h": "2 · Scenario",
        "scenario_q": "AI disruption speed",
        "scen_moderate": "Moderate disruption",
        "scen_fast": "Fast disruption",
        "scen_caption": "Predictions are estimates, not facts. We show both scenarios.",
        "trend_h": "Trend data",
        "source": "Source:",
        "retrieved": "Retrieved:",
        "pick_one": "Pick at least one skill in the sidebar to start.",
        "radar": "Future Skills Radar",
        "skill": "Skill",
        "direction": "Direction",
        "weight": "Weight",
        "sdg_h": "SDG contribution",
        "sdg_tags": "SDG tags in your shortlist",
        "sdg_roles": "role(s)",
        "ranked": "Ranked future roles",
        "ranked_caption": "Scenario: **{0}** · match score is out of 100 and fully decomposed below.",
        "coverage": "Skill coverage",
        "transfer": "Transferability",
        "trend_w": "Demand trend",
        "gap": "Gap cost",
        "have": "You already have:",
        "close": "Skills to close:",
        "none_lbl": "none",
        "pathway": "Your reskilling pathway",
        "pathway_caption": "First step towards **{0}** — ordered cheapest-first, all resources free or HRD Corp-claimable.",
        "pathway_done": "You already cover every skill for this role. Consider the next role in the ranking.",
        "compare": "Comparison across scenarios (this is how uncertainty is handled)",
        "col_role": "Role",
        "col_mod": "Moderate score",
        "col_fast": "Fast score",
        "step": "step",
        "weeks": "weeks",
        "resource": "resource",
        "footer": "Data: {0} (retrieved {1}). This tool supports human career decisions; it does not replace them.",
        "rising": "rising",
        "declining": "declining",
        "stable": "stable",
    },
    "Bahasa Malaysia": {
        "tagline": "Lumina Nusantara · SDC 2026 · Domain 1 — setiap ramalan membawa sumber dan tarikh pengambilannya; setiap peranan dipetakan kepada SDG.",
        "who": "1 · Siapa anda hari ini?",
        "how": "Bagaimana anda ingin memberitahu kami tentang diri anda?",
        "mode_upload": "Muat naik CV (PDF / TXT)",
        "mode_form": "Isi soal selidik pendek",
        "how_help": "Peraturan Domain 1: gunakan dokumen sintetik sahaja — jangan muat naik CV sebenar.",
        "drop_cv": "Letak CV di sini (sintetik sahaja)",
        "cv_help": "Teks PDF diambil secara automatik. Tiada data disimpan atau dihantar.",
        "detected": "{} kemahiran dikesan: {}",
        "not_detected": "Tiada kemahiran dikenali. Cuba soal selidik, atau tambah nama kemahiran dalam teks CV.",
        "no_cv": "Tiada CV? Gunakan salah satu profil contoh di bawah.",
        "start_profile": "Mula daripada profil",
        "custom": "Tersuai",
        "skills_edit": "Kemahiran semasa anda (boleh diubah)",
        "scenario_h": "2 · Senario",
        "scenario_q": "Kadar gangguan AI",
        "scen_moderate": "Gangguan sederhana",
        "scen_fast": "Gangguan pantas",
        "scen_caption": "Ramalan ialah anggaran, bukan fakta. Kami tunjukkan kedua-dua senario.",
        "trend_h": "Data trend",
        "source": "Sumber:",
        "retrieved": "Diambil:",
        "pick_one": "Pilih sekurang-kurangnya satu kemahiran di sisi untuk bermula.",
        "radar": "Radar Kemahiran Masa Depan",
        "skill": "Kemahiran",
        "direction": "Arah",
        "weight": "Berat",
        "sdg_h": "Sumbangan SDG",
        "sdg_tags": "Tag SDG dalam senarai pendek anda",
        "sdg_roles": "peranan",
        "ranked": "Peranan masa depan mengikut kedudukan",
        "ranked_caption": "Senario: **{0}** · skor padanan daripada 100, dipecahkan sepenuhnya di bawah.",
        "coverage": "Liputan kemahiran",
        "transfer": "Kebolehpindahan",
        "trend_w": "Trend permintaan",
        "gap": "Kos jurang",
        "have": "Anda sudah ada:",
        "close": "Kemahiran untuk ditutup:",
        "none_lbl": "tiada",
        "pathway": "Laluan latihan semula anda",
        "pathway_caption": "Langkah pertama ke **{0}** — disusun dari termurah, semua sumber percuma atau boleh dituntut HRD Corp.",
        "pathway_done": "Anda sudah meliputi semua kemahiran. Pertimbangkan peranan seterusnya.",
        "compare": "Perbandingan antara senario (inilah cara ketidakpastian dikendalikan)",
        "col_role": "Peranan",
        "col_mod": "Skor sederhana",
        "col_fast": "Skor pantas",
        "step": "langkah",
        "weeks": "minggu",
        "resource": "sumber",
        "footer": "Data: {0} (diambil {1}). Alat ini menyokong keputusan kerjaya manusia; ia tidak menggantikannya.",
        "rising": "menaik",
        "declining": "menurun",
        "stable": "stabil",
    },
    "中文": {
        "tagline": "Lumina Nusantara · SDC 2026 · Domain 1 — 每条预测都附带数据来源与抓取日期；每个岗位都对应联合国 SDG。",
        "who": "1 · 你现在的技能情况",
        "how": "你想怎么告诉我们对你的了解？",
        "mode_upload": "上传简历（PDF / TXT）",
        "mode_form": "填写简短问卷",
        "how_help": "Domain 1 规则：只能使用合成文档，禁止上传真实简历。",
        "drop_cv": "把简历拖到这里（仅限合成示范）",
        "cv_help": "自动提取 PDF 文本，不上传、不存储任何数据。",
        "detected": "识别到 {} 项技能：{}",
        "not_detected": "没有识别到技能。可以改用问卷，或在简历文本中写明技能名称（我们按固定词表匹配）。",
        "no_cv": "没有简历？用下面的示例画像试试。",
        "start_profile": "从示例画像开始",
        "custom": "自定义",
        "skills_edit": "你当前的技能（可编辑）",
        "scenario_h": "2 · 情景设置",
        "scenario_q": "AI 冲击速度",
        "scen_moderate": "温和冲击",
        "scen_fast": "快速冲击",
        "scen_caption": "预测是估计值，不是事实。我们把两种情景都给出来。",
        "trend_h": "趋势数据",
        "source": "数据来源：",
        "retrieved": "抓取日期：",
        "pick_one": "请在左侧至少选择一项技能开始。",
        "radar": "未来技能雷达",
        "skill": "技能",
        "direction": "趋势",
        "weight": "权重",
        "sdg_h": "SDG 贡献",
        "sdg_tags": "你的候选岗位覆盖的 SDG 标签数",
        "sdg_roles": "个岗位",
        "ranked": "未来岗位排名",
        "ranked_caption": "当前情景：**{0}** · 匹配分满分为 100，逐项拆解见下。",
        "coverage": "技能覆盖度",
        "transfer": "可迁移性",
        "trend_w": "需求趋势",
        "gap": "缺口成本",
        "have": "你已具备：",
        "close": "需要补齐：",
        "none_lbl": "无",
        "pathway": "你的再培训路径",
        "pathway_caption": "通往 **{0}** 的第一步 —— 由易到难排序，资源均可免费或通过 HRD Corp 报销。",
        "pathway_done": "你已覆盖该岗位所需的全部技能，可以看看排名中的下一个岗位。",
        "compare": "情景对比（我们这样处理不确定性）",
        "col_role": "岗位",
        "col_mod": "温和情景得分",
        "col_fast": "快速情景得分",
        "step": "步骤",
        "weeks": "周",
        "resource": "资源",
        "footer": "数据：{0}（抓取于 {1}）。本工具辅助人类做职业决策，不替代人的判断。",
        "rising": "上升",
        "declining": "下降",
        "stable": "持平",
    },
}


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="SkillRadar MY", page_icon="📡", layout="wide")


def render_app(lang: str) -> None:
    tx = I18N[lang]
    trend = load_trend()
    roles = apply_trend(trend)

    st.title("📡 SkillRadar MY")
    st.caption(tx["tagline"])

    with st.sidebar:
        st.header(tx["who"])

        # ---- Two intake paths required by Domain 1: CV upload OR questionnaire ----
        mode_labels = [tx["mode_upload"], tx["mode_form"]]
        intake_mode = st.radio(tx["how"], options=mode_labels, help=tx["how_help"])

        detected_from_cv: list[str] = []

        if intake_mode == mode_labels[0]:
            uploaded = st.file_uploader(
                tx["drop_cv"],
                type=["txt", "pdf", "md"],
                help=tx["cv_help"],
            )
            if uploaded is not None:
                detected_from_cv = extract_profile_from_upload(uploaded)
                if detected_from_cv:
                    st.success(tx["detected"].format(len(detected_from_cv), ", ".join(detected_from_cv)))
                else:
                    st.warning(tx["not_detected"])
            st.caption(tx["no_cv"])

        demo_choice = st.selectbox(tx["start_profile"], [tx["custom"]] + list(DEMO_PROFILES))
        if demo_choice == tx["custom"]:
            default_skills = detected_from_cv or ["customer support", "excel"]
        else:
            default_skills = DEMO_PROFILES[demo_choice]

        profile = st.multiselect(tx["skills_edit"], SKILL_OPTIONS, default=default_skills)

        st.header(tx["scenario_h"])
        scenario = st.radio(
            tx["scenario_q"],
            options=["moderate", "fast"],
            format_func=lambda x: tx["scen_moderate"] if x == "moderate" else tx["scen_fast"],
        )
        st.caption(tx["scen_caption"])

        st.divider()
        st.header(tx["trend_h"])
        st.caption(f"**{tx['source']}** {trend['source_url']}")
        st.caption(f"**{tx['retrieved']}** {trend['retrieved_at']}")
        if trend.get("note"):
            st.info(trend["note"])

    if not profile:
        st.warning(tx["pick_one"])
        st.stop()

    results = rank(profile, roles, scenario=scenario)
    top = results[0]

    col_a, col_b = st.columns((2, 1))

    with col_a:
        st.subheader(tx["radar"])
        rows = [
            {
                tx["skill"]: s["skill"],
                tx["direction"]: tx.get(s["direction"], s["direction"]),
                tx["weight"]: s["weight"],
                tx["source"]: trend["source_url"],
                tx["retrieved"]: trend["retrieved_at"],
            }
            for s in trend.get("signals", [])
            if s["skill"] in profile or s["direction"] == "rising"
        ]
        st.dataframe(rows, width="stretch", hide_index=True)

    with col_b:
        st.subheader(tx["sdg_h"])
        summary = sdg_summary(results[:4])
        st.metric(tx["sdg_tags"], sum(summary.values()))
        st.write(
            "\n".join(f"- **{k}** — {v} {tx['sdg_roles']}" for k, v in summary.items())
            or f"- {tx['none_lbl']}"
        )

    st.divider()
    st.subheader(tx["ranked"])
    st.caption(tx["ranked_caption"].format(tx["scen_moderate"] if scenario == "moderate" else tx["scen_fast"]))

    for r in results[:4]:
        c = r["components"]
        with st.expander(f"{r['score']:.1f}  ·  {r['role']}  ·  SDG {', '.join(r['sdg'])}"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(tx["coverage"], f"{c['coverage'] * 100:.0f}%")
            m2.metric(tx["transfer"], f"{c['transfer'] * 100:.0f}%")
            m3.metric(tx["trend_w"], f"{c['trend'] * 100:.0f}%")
            m4.metric(tx["gap"], f"{c['gap_cost'] * 100:.0f}%")
            st.write(f"**{tx['have']}** {', '.join(r['covered']) or '—'}")
            st.write(f"**{tx['close']}** {', '.join(r['missing']) or tx['none_lbl']}")

    st.divider()
    st.subheader(tx["pathway"])
    st.caption(tx["pathway_caption"].format(top["role"]))

    if top["missing"]:
        plan = [
            {
                tx["step"]: p["step"],
                tx["skill"]: p["skill"],
                tx["weeks"]: p["weeks"],
                tx["resource"]: p["resource"],
            }
            for p in pathway(top)
        ]
        st.table(plan)
    else:
        st.success(tx["pathway_done"])

    st.divider()
    with st.expander(tx["compare"]):
        moderate = rank(profile, roles, scenario="moderate")
        fast = rank(profile, roles, scenario="fast")
        st.dataframe(
            [
                {
                    tx["col_role"]: m["role"],
                    tx["col_mod"]: m["score"],
                    tx["col_fast"]: f["score"],
                    "Δ": round(f["score"] - m["score"], 1),
                }
                for m, f in zip(moderate, fast)
            ],
            width="stretch",
            hide_index=True,
        )

    st.caption(tx["footer"].format(trend["source_url"], trend["retrieved_at"]))


# --------------------------------------------------------------------------- #
# Language selector (top-right): English / Bahasa Malaysia / 中文
# --------------------------------------------------------------------------- #

LANGUAGE_OPTIONS = ["English", "Bahasa Malaysia", "中文"]

_, lang_col = st.columns((5, 1))
with lang_col:
    lang = st.selectbox(
        "Language / Bahasa / 语言",
        options=LANGUAGE_OPTIONS,
        index=0,
        label_visibility="collapsed",
        key="language_selector",
    )

render_app(lang)
