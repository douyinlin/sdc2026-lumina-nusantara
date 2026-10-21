"""Pure presentation helpers. No matching, scoring, storage or network calls."""
from html import escape
from pathlib import Path

CSS_PATH = Path(__file__).resolve().parent / "post_selection.css"

COPY = {
    "en": {
        "choose": "Choose your role", "profile": "Build your profile", "results": "Explore your results",
        "intake_title": "Start with what you know.",
        "results_title": "Make your next step a clear one.",
        "intake_note": "Your context and skills shape the recommendations. You stay in control.",
        "results_note": "Explore the evidence, understand the fit, then choose what to learn next.",
        "score": "Match score", "weighted": "Weighted skill coverage",
        "lower": "Lower is better", "weeks": "weeks", "details": "Detailed figures",
        "path": "Your learning route", "selected": "Skills in your profile",
        "skills_note": "Choose a few strengths that best describe you; you do not need to fill every category.",
        "market_note": "Market evidence and sources are available below. Scores remain prototype estimates, not hiring probabilities.",
        "rank_note": "Ranked by the existing weighted model. Open a role to inspect its five inputs; the score is not a hiring probability.",
    },
    "zh": {
        "choose": "选择你的身份", "profile": "建立技能档案", "results": "探索分析结果",
        "intake_title": "从你已经掌握的能力开始。",
        "results_title": "让下一步，更清晰。",
        "intake_note": "你的背景与技能决定推荐方向；每一步都由你选择。",
        "results_note": "先看匹配，再理解依据，最后选择下一项值得学习的技能。",
        "score": "岗位匹配分", "weighted": "加权技能覆盖率",
        "lower": "越低越好", "weeks": "周", "details": "查看详细数据",
        "path": "你的学习路线", "selected": "你的技能档案",
        "skills_note": "选几项最能代表你的优势即可，不必填满每个分类。",
        "market_note": "下方保留了市场证据与来源。评分仍为原型估计，不是录用概率。",
        "rank_note": "沿用原有加权模型排序。展开岗位可查看五项评分输入；分数不是录用概率。",
    },
    "ms": {
        "choose": "Pilih peranan", "profile": "Bina profil anda", "results": "Terokai hasil",
        "intake_title": "Mulakan dengan kemahiran anda.",
        "results_title": "Jadikan langkah seterusnya lebih jelas.",
        "intake_note": "Latar belakang dan kemahiran anda membentuk cadangan. Anda kekal mengawal pilihan.",
        "results_note": "Lihat bukti, fahami padanan, kemudian pilih kemahiran untuk dipelajari.",
        "score": "Skor padanan", "weighted": "Liputan kemahiran berwajaran",
        "lower": "Lebih rendah lebih baik", "weeks": "minggu", "details": "Angka terperinci",
        "path": "Laluan pembelajaran anda", "selected": "Kemahiran dalam profil anda",
        "skills_note": "Pilih kekuatan utama anda; tidak perlu mengisi setiap kategori.",
        "market_note": "Bukti pasaran dan sumber tersedia di bawah. Skor ialah anggaran prototaip, bukan kebarangkalian mendapat kerja.",
        "rank_note": "Disusun oleh model berwajaran sedia ada. Buka peranan untuk melihat lima input; skor bukan kebarangkalian mendapat kerja.",
    },
}

ICONS = {
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5z"/>',
    "person": '<circle cx="12" cy="8" r="3"/><path d="M5 21v-3a7 7 0 0 1 14 0v3"/>',
    "chart": '<path d="M4 4v16h16M8 15v-4m5 4V7m5 8v-6"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
    "route": '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="19" r="2"/><path d="M8 5h7a4 4 0 0 1 0 8H9a3 3 0 0 0 0 6h7"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
}


def copy_for(lang: str) -> dict[str, str]:
    return COPY.get(lang, COPY["en"])


def icon(name: str) -> str:
    return (
        '<svg class="srui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">'
        + ICONS.get(name, ICONS["compass"]) + "</svg>"
    )


def brand() -> str:
    return f'<div class="srui-brand">{icon("compass")}<span>SkillRadar <b>MY</b></span></div>'


def flow_header(stage: str, flow: str, lang: str) -> str:
    text = copy_for(lang)
    result = stage.endswith("_results")
    current = 2 if result else 1
    items = []
    for index, key in enumerate(("choose", "profile", "results")):
        state = "done" if index < current else "active" if index == current else "pending"
        mark = icon("check") if state == "done" else str(index + 1)
        aria = ' aria-current="step"' if state == "active" else ""
        items.append(
            f'<li class="srui-step {state}"{aria}><span class="srui-step-number">{mark}</span>'
            f'<span>{escape(text[key])}</span></li>'
        )
    title = text["results_title" if result else "intake_title"]
    note = text["results_note" if result else "intake_note"]
    return (
        '<section class="srui-flow">'
        f'<p class="srui-eyebrow">{escape(flow)}</p>'
        f'<ol class="srui-stepper">{"".join(items)}</ol>'
        f'<h1>{escape(title)}</h1><p class="srui-lede">{escape(note)}</p></section>'
    )


def skill_chips(labels: list[str], variant: str = "") -> str:
    return '<div class="srui-chips">' + "".join(
        f'<span class="srui-chip {escape(variant, quote=True)}">{escape(label)}</span>'
        for label in labels
    ) + "</div>"


def score_panel(score: float, components: list[tuple[str, float]], lang: str) -> str:
    """Display existing 0–1 model inputs; never recalculate the score."""
    text = copy_for(lang)
    meters = []
    for label, value in components:
        pct = value * 100
        width = max(0, min(100, pct))
        meters.append(
            '<div class="srui-meter-row">'
            f'<div class="srui-meter-label"><span>{escape(label)}</span><b>{pct:.0f}%</b></div>'
            f'<div class="srui-meter" role="meter" aria-label="{escape(label, quote=True)}" '
            f'aria-valuenow="{pct:.1f}" aria-valuemin="0" aria-valuemax="100">'
            f'<span style="--meter-width:{width:.2f}%"></span></div></div>'
        )
    return (
        '<div class="srui-scorecard"><div class="srui-score">'
        f'{icon("chart")}<span>{escape(text["score"])}</span>'
        f'<strong>{score:.1f}<small> / 100</small></strong></div>'
        '<div class="srui-meter-list">' + "".join(meters) + "</div></div>"
    )


def learning_path(rows: list[tuple[int, str, int]], lang: str) -> str:
    """Preserve the engine's order and duration, including nonconsecutive steps."""
    text = copy_for(lang)
    cards = []
    for step, skill, weeks in rows:
        cards.append(
            '<li class="srui-path-step">'
            f'<span class="srui-path-number">{step:02d}</span>'
            f'<div><h4>{escape(skill)}</h4><span class="srui-duration">'
            f'{icon("clock")}{weeks} {escape(text["weeks"])}</span></div></li>'
        )
    return (
        f'<div class="srui-path-title">{icon("route")}{escape(text["path"])}</div>'
        '<ol class="srui-path">' + "".join(cards) + "</ol>"
    )
