"""Build the two SDC 2026 submission PDFs for Lumina Nusantara.

Run:  python tools/build_pdfs.py
Outputs:
    submission/SDC2026_LuminaNusantara_Preliminary.pdf
    submission/SDC2026_LuminaNusantara_TechDeclaration.pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "submission"
OUT.mkdir(exist_ok=True)

TEAM = "Lumina Nusantara"
LEADER = "DU YULIN"
EMAIL = "CYS2609009@xmu.edu.my"
PHONE = "+60 11-1798 1756"
UNIVERSITY = "Xiamen University Malaysia (XMUM)"
MEMBERS = 5
DOMAIN = "Domain 1 — The Aiversecity Future-Ready Workforce Domain"
SDG = "SDG 4 — Quality Education (sub-target 4.4, with 8.5)"
PROJECT = "SkillRadar MY"
LIVE = "https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app"
REPO = "https://github.com/douyinlin/sdc2026-lumina-nusantara"

OLIVE = colors.HexColor("#8A9A5B")
DARK = colors.HexColor("#333333")
LIGHT = colors.HexColor("#EEF3E6")

ss = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body", parent=ss["Normal"], fontName="Helvetica", fontSize=9.6, leading=14,
    textColor=DARK, alignment=TA_LEFT, spaceAfter=6,
)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=8.4, leading=11.5)
NOTE = ParagraphStyle(
    "Note", parent=BODY, fontSize=8.6, leading=12, textColor=colors.HexColor("#555555"),
    leftIndent=6, rightIndent=6,
)
H1 = ParagraphStyle(
    "H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21,
    textColor=DARK, spaceBefore=14, spaceAfter=4,
)
H2 = ParagraphStyle(
    "H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=15,
    textColor=OLIVE, spaceBefore=10, spaceAfter=3,
)
H3 = ParagraphStyle(
    "H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=9.8, leading=13,
    textColor=DARK, spaceBefore=6, spaceAfter=2,
)
TITLE = ParagraphStyle(
    "Title", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=30, leading=36,
    textColor=DARK, spaceAfter=6,
)
SUB = ParagraphStyle("Sub", parent=BODY, fontSize=11, leading=15, textColor=OLIVE)


def rule(width: float = 165 * mm, color=OLIVE) -> Table:
    t = Table([[""]], colWidths=[width], rowHeights=[1.6])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color)]))
    return t


def kv_table(rows, col_widths=(48 * mm, 117 * mm)) -> Table:
    data = [[Paragraph(f"<b>{k}</b>", SMALL), Paragraph(v, SMALL)] for k, v in rows]
    t = Table(data, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
            ]
        )
    )
    return t


def grid_table(header, rows, col_widths) -> Table:
    data = [[Paragraph(f"<b>{h}</b>", SMALL) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), SMALL) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                ("BACKGROUND", (0, 0), (-1, 0), OLIVE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAF7")]),
            ]
        )
    )
    return t


def bullets(items, style=SMALL) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(i, style), leftIndent=10) for i in items],
        bulletType="bullet", start="•", leftIndent=12, spaceAfter=6,
    )


def page_footer(canvas, doc, label: str) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.6)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawString(20 * mm, 12 * mm, label)
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


# --------------------------------------------------------------------------- #
# Content
# --------------------------------------------------------------------------- #

def para(text):
    return Paragraph(text, BODY)


def section(title, *texts):
    return (title, [para(t) for t in texts])


def signature():
    return KeepTogether([para("Leader signature (after review): __________________________"),
                         para("Name: DU YULIN"), para("Actual signing date: __________________________")])


PRELIM_SECTIONS = [
    ("1. TEAM AND PROJECT OVERVIEW", [kv_table([
        ("Team", TEAM), ("Domain", DOMAIN), ("SDG track", SDG), ("Project", PROJECT),
        ("Leader", LEADER), ("Contact", EMAIL + " / " + PHONE),
        ("University", UNIVERSITY), ("Members", "5: DU YULIN; GAO TANGLINYUE; ZHENG QUANYING; WU ZHUOLI; ZHANG BORAN")])]),
    section("2. EXECUTIVE SUMMARY &amp; PROBLEM STATEMENT",
        "<b>2.1 Problem context</b><br/>Malaysian workers and graduates need to understand how changing demand affects their next learning decision. The official SDC Domain 1 brief cites 56% AI-tool adoption versus 26% formal training and a MOSTI estimate of over 600,000 workers needing reskilling. These are secondary citations from the competition brief, not measurements collected by this team. Static course lists do not explain why a role fits, what skills are missing, or how the recommendation changes under uncertainty. We target workers, graduates, HR teams and career centres who need a transparent starting point for reskilling. The prototype supports guidance rather than predicting employment or making hiring decisions.",
        "<b>2.2 Proposed solution and current implementation</b><br/>SkillRadar MY accepts a questionnaire or synthetic text CV. A local keyword and alias parser maps skills to a team-curated catalogue; it does not implement a complete O*NET/ESCO identifier mapping. Dated JSON snapshots separate DOSM occupation-level observations, JobStreet/Randstad named-skill signals and WEF global forecasts. Validated manual import supports updating selected snapshots; automatic collection is future work. Five visible scoring components cover skills, role focus, transferability, demand and gap cost. Ordered learning steps link to recorded resources or search routes where coverage is absent. Hours and fees still require verification. Role and skill SDG mappings are team interpretations. Moderate and fast-disruption scenarios expose sensitivity to assumptions. The current application uses Streamlit, Python, JSON and session state. It calls no external model API and requires no GPU. Replit usage screenshots are retained; Streamlit Community Cloud provides the public demo. Automated ingestion, semantic parsing and a database are future options, not implemented features."),
    section("3. TECHNICAL ARCHITECTURE &amp; IMPLEMENTATION PLAN",
        "<b>3.1 Architecture</b><br/>Synthetic profile / questionnaire -> Streamlit UI -> local skill extractor -> five-component matching engine -> learning pathway and SDG display. The engine reads team-curated JSON catalogues and dated trend snapshots. A human reviews source material and runs the validation/import command. There is no database or external inference service on the request path. Replit is the documented development workspace; the live URL uses Streamlit Community Cloud. No RunPod endpoint is used.",
        "<b>3.2 Design thinking and deployment</b><br/>The problem definition draws on the Domain 1 brief and public labour-market reports. This revision does not claim completed interviews or user pilots: evidence for the previous five-person claims has not been supplied. The implemented flows expose missing skills, score components, evidence sources, scenarios and learning steps. Repository tests and development logs document local regression checks; these are not substitutes for independent user validation. Before submission the team should check the deployed flow using synthetic data and restore judge access to the Replit project. A future pilot should observe users completing the same task with and without the prototype and record time, relevance ratings and confusion points. Deployment and human review must be confirmed by the team."),
    section("4. PRELIMINARY ENVIRONMENTAL &amp; SDG IMPACT FRAMEWORK",
        "<b>Targets:</b> SDG 4.4 (employment-relevant skills), with 8.5 (decent work). Skill mappings express intended contribution, not measured UN impact.",
        "<b>Baseline:</b> The brief reports 56% adoption and 26% training, a 30-percentage-point context gap. A product-specific time-to-plan baseline has not yet been measured. The previous 3-8 week / median four-week interview baseline is withdrawn pending evidence.",
        "<b>KPIs and proposed Phase 2 targets:</b> Measure time to produce a sourced plan and participant-rated top-three relevance. Proposed pilot: at least 10 consenting adult testers using synthetic profiles; target median completion within five minutes and at least 70% rating one top-three role at least 4/5 for relevance. Target 20% lower median task time against an equivalent manual-search task, if a valid baseline is collected before the final. Audit 100% of displayed role/skill recommendations for a source or explicit team-assumption label. These are targets, not results. Longer-term learning completion is outside the final-round evaluation window."),
    section("5. ELIGIBILITY &amp; READINESS CHECKLIST",
        "SDG mapping and an implemented prototype are present. Team confirmation remains required for mandatory workshop attendance, official registration eligibility, deployed end-to-end testing, sponsor access, third-party terms and final submission completeness. Video is pending. This unsigned revision does not pre-check those attestations."),
    section("6. IP &amp; ORIGINALITY DECLARATION",
        "<b>6.1 Prior-owned work:</b> Previous team declaration: none. Leader must reconfirm before signing; repository history alone cannot establish originality.",
        "<b>6.2 Third-party materials:</b> Python (PSF), Streamlit (Apache 2.0), pandas / NumPy (BSD 3-Clause), PyArrow (Apache 2.0), Matplotlib (Matplotlib license), ReportLab (BSD) and public-source references are used. The Technical Declaration inventories current data and development tools. Public availability is not a blanket reuse license; source-specific terms require team review.",
        "<b>6.3 Employment-related IP:</b> Previous team declaration: none. Each member must reconfirm any employment, internship or consulting restrictions."),
    ("7. DECLARATION", [para("By signing after review, the leader confirms the final submission is accurate and original to the best of the team's knowledge. This revised document has not been signed; the previous signature is not carried over to changed statements."), signature()]),
]

TECH_SECTIONS = [
    ("1. TEAM AND PROJECT OVERVIEW", [kv_table([("Team / project", TEAM + " / " + PROJECT), ("Leader", LEADER), ("Contact", EMAIL + " / " + PHONE), ("University", UNIVERSITY), ("Live prototype", LIVE), ("Public repository", REPO)])]),
    section("2. ARCHITECTURE &amp; TECHNOLOGY STACK",
        "<b>2.1 Architecture</b><br/>Streamlit collects a synthetic profile and calls local Python modules for keyword extraction, five-component matching, learning pathways and SDG interpretation. JSON files supply roles, courses and dated trend snapshots. Session state holds the current interaction. A validated manual import updates trend snapshots after human review. There is no scheduled ingestion, relational database, external LLM or GPU inference. Scenario and scoring coefficients are prototype heuristics, not measured hiring probabilities.",
        "<b>2.2 Runtime libraries</b><br/>Validated local environment: Python 3.12 (PSF). Direct requirements: Streamlit 1.66.0 (Apache 2.0), pandas 3.0.6 (BSD 3-Clause), NumPy 2.5.4 (BSD 3-Clause), PyArrow 26.0.0 (Apache 2.0), Matplotlib 3.11.2 (Matplotlib license). Development/documentation utilities include unittest, mypy, Playwright, ReportLab, pypdf and pypdfium2. Exact ancillary versions and provider terms require final inventory confirmation. These utilities are not inference models."),
    section("3. APIs &amp; CLOUD SERVICES",
        "<b>3.1 External APIs:</b> No external model API is called by the product. Public report pages are source references, not continuously consumed API feeds. Firecrawl was used during development/review for web retrieval, not by the runtime app.",
        "<b>3.2 Services:</b> Streamlit Community Cloud hosts the demo; GitHub hosts public code; Replit is evidenced as a development workspace. Current account plans, deployment region and deployed commit must be confirmed from account settings; they are not inferred from URLs. Replit project: https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app. Unauthenticated access on 23 October returned Page not found / owner invitation required."),
    section("4. AI TOOLS, MODELS &amp; DATASETS",
        "<b>4.1 Runtime models:</b> None. Skill extraction and matching use team-authored rules. The catalogue is not a verified complete O*NET/ESCO mapping.",
        "<b>4.2 Data:</b> DOSM Q1/Q2 2026 occupation observations; WEF Future of Jobs 2025 global forecast; JobStreet/Randstad 2025 reported skill signals; role-level Malaysian references including PIKOM; team-curated role/skill and SDG catalogues; 36 course-link records; synthetic profiles and sample CV. See the source inventory appendix for URLs. Course costs/durations and source-specific reuse terms require verification. Team-authored code is Apache 2.0; this does not relicense third-party reports. No real personal CV data is intended for use.",
        "<b>4.3 Development AI:</b> OpenAI Codex was used extensively for code review, implementation, debugging, tests and documentation. ChatGPT assisted project planning and written guidance. DeepSeek-based assistant and GitHub Copilot were declared in the earlier team document (scaffolding/documentation and inline completion respectively); the team must confirm their actual usage and model versions. Product subscription names are not exact model identifiers. No unsupported model version is asserted.",
        "<b>Review statement:</b> Automated checks and local browser checks are recorded in team/DEVELOPMENT_LOG.md. These do not prove all facts, courses or AI output were manually verified. Team review of code, data, assertions and final documents remains required. No claim is made that every change received independent pull-request review."),
    section("5. SPONSOR-PROVIDED RESOURCES",
        "Replit was used as evidenced by the appended historical workspace screenshots. Those screenshots do not establish that the latest GitHub commit runs there. Restore judge access to project history or provide an acceptable live Replit deployment URL before submission. No RunPod endpoint or GPU is used by the current app. Replit is replaceable as a Python development environment; the current public demo runs on Streamlit Community Cloud. Account plan and sponsor credit usage require owner confirmation."),
    section("6. SECURITY, PRIVACY &amp; RESPONSIBLE USE",
        "<b>6.1 Privacy:</b> Use only synthetic CVs and public or synthetic data. Uploaded text is parsed in memory; the application does not intentionally persist CVs in a database. Hosting provider/session behavior remains subject to provider terms. The app requires no inference API secret. Repository secret review and provider settings remain team responsibilities.",
        "<b>6.2 Limitations:</b> Source lag, selection bias and incomplete course coverage affect recommendations. Keyword parsing supports plain text and limited text PDFs, not OCR or semantic understanding. Fixed catalogues can still contain incorrect roles, links or metadata. Prices and durations are not fully verified. Scenario coefficients and skill-to-SDG links are team interpretations. Fairness and user impact have not been established. The tool assists career exploration and must not make hiring decisions."),
    section("7. COMPLIANCE &amp; READINESS",
        "Before signing: confirm actual tools and versions, source terms, team review, workshop attendance, no exposed credentials, committee collaborator access, Replit proof accessibility and the deployed user flow. Add the YouTube video separately. Unresolved items are tracked in submission/OWNER_ACTIONS.md; they are not marked completed in this revision."),
    ("8. DECLARATION", [para("The leader must review and sign the final accurate declaration. The old signature and future date have not been reused on revised content."), signature()]),
]

def build(path: Path, doc_title: str, headline: str, subtitle: str, sections,
          footer: str, intro: list) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
        title=doc_title, author=f"{TEAM} · {LEADER}", subject="SDC 2026 Hackathon",
    )

    story: list = [
        Spacer(1, 30 * mm),
        Paragraph("SDC", TITLE),
        Paragraph(headline, ParagraphStyle("h", parent=TITLE, fontSize=24, leading=30)),
        Spacer(1, 4),
        Paragraph(subtitle, SUB),
        Spacer(1, 10),
        rule(),
        Spacer(1, 12),
        Paragraph(f"<b>{TEAM}</b> · {DOMAIN}", BODY),
        Paragraph(f"SDG Track: {SDG}", BODY),
        Paragraph(f"Team Leader: {LEADER} · {UNIVERSITY}", BODY),
        Spacer(1, 8),
        Paragraph(f"Live prototype: {LIVE}", SMALL),
        Paragraph(f"Code repository: {REPO}", SMALL),
        Spacer(1, 14),
        Paragraph("Submission deadline: 25 October 2026, 07:59:59 UTC+8", ParagraphStyle(
            "dl", parent=BODY, textColor=OLIVE, fontName="Helvetica-Bold")),
        Spacer(1, 10),
    ]
    story.extend(intro)
    story.append(PageBreak())

    for heading, flowables in sections:
        block = [Paragraph(heading, H2), rule(165 * mm, colors.HexColor("#DDDDDD")), Spacer(1, 4)]
        story.append(KeepTogether(block[:2]))
        story.append(Spacer(1, 2))
        story.extend(flowables)
        story.append(Spacer(1, 8))

    doc.build(
        story,
        onFirstPage=lambda c, d: page_footer(c, d, f"{TEAM} · SDC 2026 · {footer}"),
        onLaterPages=lambda c, d: page_footer(c, d, f"{TEAM} · SDC 2026 · {footer}"),
    )
    print(f"wrote {path}")


def append_evidence():
    import json
    from xml.sax.saxutils import escape
    from pypdf import PdfReader, PdfWriter
    urls = set()
    def collect(value):
        if isinstance(value, dict):
            for item in value.values(): collect(item)
        elif isinstance(value, list):
            for item in value: collect(item)
        elif isinstance(value, str) and value.startswith("https://"):
            urls.add(value)
    for path in (ROOT / "data").rglob("*.json"):
        collect(json.loads(path.read_text(encoding="utf-8")))
    import tempfile
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        appendix = Path(temp) / "appendix.pdf"
        content = [para("Appendix A: Public source and resource inventory"), para("URLs recorded in the current JSON catalogue. Inclusion does not certify accuracy, licensing, fees or durations; these remain subject to team review.")]
        content += [Paragraph(escape(url), SMALL) for url in sorted(urls)]
        content += [PageBreak(), para("Appendix B: Historical Replit evidence"), para("The following three pages are preserved historical screenshots. Their original captions refer to the version captured at that time, not the latest GitHub commit. They do not establish current judge access or current deployment equivalence. Project: https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app. Owner must restore access and verify the current version before signing.")]
        SimpleDocTemplate(str(appendix), pagesize=A4, leftMargin=20*mm, rightMargin=20*mm).build(content)
        target = OUT / "SDC2026_LuminaNusantara_TechDeclaration.pdf"
        writer = PdfWriter()
        for source in [target, appendix, OUT / "REPLIT PROOF OF USE.pdf"]:
            writer.append(PdfReader(source))
        writer.write(str(target))


def main() -> None:
    prelim_intro = [
        Paragraph(
            "Phase 1 — Preliminary Project Proposal. Answers below follow the official template order "
            "and the stated word limits. Revised unsigned copy: leader review required.", NOTE),
    ]
    build(
        OUT / "SDC2026_LuminaNusantara_Preliminary.pdf",
        f"SDC2026 {TEAM} Preliminary",
        "Hackathon · Phase 1",
        "Preliminary Project Proposal",
        PRELIM_SECTIONS,
        "Preliminary Project Proposal",
        prelim_intro,
    )

    tech_intro = [
        Paragraph(
            "Technical Tools Declaration. Revised unsigned copy; "
            "recorded the actual status. Leader review and signature remain required.", NOTE),
    ]
    build(
        OUT / "SDC2026_LuminaNusantara_TechDeclaration.pdf",
        f"SDC2026 {TEAM} TechDeclaration",
        "Hackathon · Technical",
        "Technical Tools Declaration",
        TECH_SECTIONS,
        "Technical Tools Declaration",
        tech_intro,
    )


if __name__ == "__main__":
    main()
    append_evidence()
