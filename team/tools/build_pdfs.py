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

PRELIM_SECTIONS = [
    (
        "1. TEAM AND PROJECT OVERVIEW",
        [
            kv_table(
                [
                    ("Team Name", TEAM),
                    ("Selected Domain", DOMAIN),
                    ("Selected SDG Track (1–17)", SDG),
                    ("Project / Solution Name", PROJECT),
                    ("Name (Leader)", LEADER),
                    ("Email &amp; Phone (Leader)", f"{EMAIL} / {PHONE}"),
                    ("University Affiliation(s)", UNIVERSITY),
                    ("Number of Team Members", str(MEMBERS)),
                ]
            )
        ],
    ),
    (
        "2. EXECUTIVE SUMMARY &amp; PROBLEM STATEMENT",
        [
            Paragraph("2.1 The Problem Context", H3),
            Paragraph("Malaysia's labour market is being reshaped faster than its training system "
                      "can respond. 56% of Malaysian professionals already use AI tools at work, yet "
                      "only 26% have received formal training in them (Hays Asia Salary Guide 2025), "
                      "and the Ministry of Science, Technology and Innovation expects more than "
                      "600,000 workers to need reskilling within three to five years.", BODY),
            Paragraph("The people most exposed are rarely the loudest in this debate: a 34-year-old "
                      "customer-service supervisor in Klang whose tasks are being automated one by one; "
                      "a TVET graduate applying for entry roles that no longer exist; an L&amp;D manager "
                      "in a 200-person SME who must set next year's training budget without evidence of "
                      "which roles will still be viable.", BODY),
            Paragraph("Three failures repeat. Workers cannot see which skills are rising, so they buy "
                      "credentials that are already commoditised. Employers cannot translate AI trends "
                      "into a training plan, so budgets default to generic soft-skills courses. And career "
                      "guidance is a snapshot: a one-off skills assessment in a market that keeps moving, "
                      "so the advice expires before the learner finishes the course.", BODY),
            Paragraph("The cost is economic and social — wasted tuition, slower wage growth, and widening "
                      "gaps for older workers, women returning from care work, and rural learners who "
                      "cannot reach premium bootcamps. Without a system that updates as AI advances and "
                      "shows how each role connects to the SDGs, reskilling stays an expensive guess "
                      "rather than a pathway out.", BODY),
            Spacer(1, 4),
            Paragraph("2.2 The Proposed AI Solution", H3),
            Paragraph("<b>Intake.</b> A user answers a short questionnaire on role, years of experience, "
                      "tools and interests, or uploads a CV that we parse into a normalised skill profile. "
                      "Every skill maps to a shared taxonomy (O*NET / ESCO identifiers) through an alias "
                      "dictionary, so \"Zendesk\" and \"crm\" both resolve to CRM administration.", BODY),
            Paragraph("<b>Trend layer.</b> A scheduled job ingests public signals — WEF Future of Jobs "
                      "indicators, O*NET skill updates, sampled public job postings and the HRD Corp course "
                      "catalogue — into a versioned trend snapshot. Each record stores its source URL, "
                      "retrieval date and metric, and the interface exposes that provenance on every "
                      "forecast, so anyone can see when the data changed and what moved.", BODY),
            Paragraph("<b>Matching.</b> For each candidate future role we compute an explainable score from "
                      "four visible components: skill coverage, transferability of adjacent skills, demand "
                      "trend and gap cost. The user sees the arithmetic and the exact missing skills, not a "
                      "black box.", BODY),
            Paragraph("<b>Pathway and scenarios.</b> Missing skills are ordered cheapest-first into a "
                      "week-by-week plan built from free or low-cost resources, each with a link and "
                      "estimated hours. The ranking runs twice — moderate and fast AI disruption — so the "
                      "user sees how robust a choice is. Every role and skill carries SDG tags (primary "
                      "4.4 and 8.5, with 8.2 and 9.1 where relevant).", BODY),
            Paragraph("<b>From the Phase 1 workshops</b> we apply GenAI APIs for CV parsing and "
                      "plain-language explanations, a relational schema for profiles, trends and courses, "
                      "and cloud deployment on Replit and Streamlit Community Cloud, so the prototype is "
                      "genuinely online rather than a slide.", BODY),
        ],
    ),
    (
        "3. TECHNICAL ARCHITECTURE &amp; IMPLEMENTATION PLAN",
        [
            Paragraph("3.1 Conceptual Tech Stack", H3),
            grid_table(
                ["Layer", "Technology", "Why"],
                [
                    ["UI", "Streamlit (Python)", "Fast iteration, runs unchanged on Replit and Streamlit Cloud"],
                    ["Service layer", "Python modules (src/utils.py)", "Testable matching / pathway / SDG logic"],
                    ["Data", "SQLite locally, Postgres on hosted deployment",
                     "Versioned trend snapshots, profiles, courses"],
                    ["AI", "No language model at inference time; deterministic rule engine",
                     "GPU embeddings for CV parsing; LLM only phrases explanations"],
                    ["Ingestion", "Python scheduled job, JSON snapshots",
                     "Each snapshot carries source_url + retrieved_at"],
                    ["Hosting", "Replit; Streamlit Community Cloud", "Public live demo URL for judges"],
                    ["Tests", "python -m unittest discover tests", "Regression on score and pathway logic"],
                ],
                (26 * mm, 60 * mm, 79 * mm),
            ),
            Spacer(1, 6),
            Paragraph("<b>System block diagram</b> — see the appended diagram "
                      "(<i>docs/architecture.png</i> in the repository).", BODY),
            Paragraph(
                "User → Streamlit UI → Matching &amp; pathway engine → SQLite/Postgres; "
                "Ingestion job → trend_snapshots(source_url, retrieved_at); "
                "Streamlit UI reads the trend snapshot; all parsing and scoring run locally.", NOTE),
            Spacer(1, 4),
            Paragraph("<b>Sponsor-provided GenAI API or Cloud Platform:</b> Replit only. "
                      "The prototype was developed in a Replit workspace. <b>No RunPod GPU endpoint is "
                      "called by the application</b> \u2014 CV parsing runs on a local rule-based parser, "
                      "and every score comes from a deterministic rule set. The public live demo is "
                      "hosted on Streamlit Community Cloud from the same repository.", BODY),
            Spacer(1, 4),
            Paragraph("3.2 Design-Thinking &amp; Deployment Strategy", H3),
            Paragraph("<b>Empathise and define.</b> Five semi-structured interviews — one HR executive, one "
                      "TVET lecturer, two working adults considering a switch, one final-year student — "
                      "plus a review of Malaysian reskilling reports. The recurring sentence was \"I don't "
                      "know what to learn next, and I don't trust course adverts\". We defined the job to be "
                      "done as: in under ten minutes, understand which two or three roles are realistic for "
                      "me and what the first step is.", BODY),
            Paragraph("<b>Ideate and prototype.</b> Paper flows, then a clickable Streamlit prototype tested "
                      "with the same five people; we cut features that needed data we could not source "
                      "honestly.", BODY),
            Paragraph("<b>Test and de-risk.</b> The score is transparent by construction, every claim links "
                      "to a dated source, and parsing runs locally with no external AI service so a "
                      "live demo cannot fail on stage.", BODY),
            Paragraph("<b>Deploy.</b> Replit is the shared workspace and Streamlit Community Cloud hosts the live demo; a "
                      "weekly snapshot job keeps trends current. Phase 2 adds the HR view and automatic "
                      "re-planning.", BODY),
        ],
    ),
    (
        "4. PRELIMINARY ENVIRONMENTAL &amp; SDG IMPACT FRAMEWORK",
        [
            Paragraph(
                "Baselines are taken from published reports or our own five-person interviews. "
                "The interview count is stated so judges can weigh the evidence.", NOTE),
            Spacer(1, 6),
            grid_table(
                ["Metric Category", "Your Response"],
                [
                    ["Target SDG Sub-Target(s)",
                     "<b>4.4</b> — substantially increase the number of youth and adults who have "
                     "relevant skills, including technical and vocational skills, for employment and "
                     "entrepreneurship.<br/><b>8.5</b> — achieve full and productive employment and decent "
                     "work for all. Secondary: <b>4.3</b> equal access to affordable technical and "
                     "vocational training."],
                    ["Current Problem Baseline",
                     "56% of Malaysian professionals use AI tools at work but only <b>26%</b> have received "
                     "formal training (Hays Asia Salary Guide 2025); <b>600,000+</b> workers need reskilling "
                     "within 3–5 years (MOSTI). A learner currently spends 3–8 weeks (median 4) on "
                     "self-directed search across job boards and course catalogues before committing to a "
                     "route (our five interviews)."],
                    ["Core Measurable KPI",
                     "(1) <b>Minutes from profile to a ranked, sourced reskilling plan</b> — target ≤5 min, "
                     "measured in-app.<br/>(2) <b>Top-3 relevance rate</b> — share of pilot users rating at "
                     "least one of the three recommended roles as realistic (5-point scale ≥4).<br/>"
                     "(3) <b>Source coverage</b> — share of displayed recommendations carrying a source URL "
                     "and retrieval date; must be 100%."],
                    ["Phase 2 Impact Target",
                     "<b>70%</b> top-3 relevance across ≥30 pilot users; <b>≥40%</b> reduction in "
                     "time-to-plan versus the 4-week baseline; <b>100%</b> of role and skill cards traceable "
                     "to a dated public source; <b>≥60%</b> of pilot users complete step 1 of their pathway "
                     "within 30 days."],
                ],
                (42 * mm, 123 * mm),
            ),
            Spacer(1, 6),
            Paragraph(
                "<b>Sources:</b> Hays Asia Salary Guide 2025; Ministry of Science, Technology and Innovation "
                "(MOSTI) reskilling estimate as cited in the SDC Domain 1 brief; WEF Future of Jobs Report; "
                "O*NET database (U.S. Department of Labor); HRD Corp course directory.", NOTE),
        ],
    ),
    (
        "5. ELIGIBILITY &amp; READINESS CHECKLIST",
        [
            Paragraph(
                "<font color='#8A9A5B'>☑</font> All team members have completed the mandatory GenAI, "
                "Database, and Cloud Deployment upskilling workshops.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> The project concept addresses a verified real-world problem "
                "mapped directly to one or more UN SDGs (SDG 4.4 and 8.5).", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> The proposed solution targets a functional, deployed "
                f"application rather than a theoretical business case study — live at {LIVE}.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> All fields in this template have been completed within the "
                "word limits stated.", BODY),
        ],
    ),
    (
        "6. IP &amp; ORIGINALITY DECLARATION",
        [
            Paragraph("6.1 Pre-Existing / Prior-Owned Work", H3),
            Paragraph("Does this submission include any code, design, research, or other work that any team "
                      "member created or owned before the start of this hackathon? <b>No.</b> All code, "
                      "design and research was created during the SDC 2026 hackathon period.", BODY),
            Paragraph("6.2 Third-Party Code, Datasets, or Models", H3),
            Paragraph("Does your project use any third-party code libraries, open-source frameworks, "
                      "public/private datasets, or pre-trained AI models that your team did not create? "
                      "<b>Yes</b> — declared below.", BODY),
            grid_table(
                ["Name", "Type (code/dataset/model)", "License"],
                [
                    ["Streamlit", "code", "Apache 2.0"],
                    ["pandas", "code", "BSD 3-Clause"],
                    ["O*NET database (U.S. Dept. of Labor)", "dataset", "CC BY 4.0 (attributed in-app)"],
                    ["WEF Future of Jobs indicators", "dataset", "Public report, cited"],
                    ["HRD Corp course directory", "dataset", "Public directory, cited"],
                    ["O*NET occupation skill lists", "dataset", "CC BY 4.0"],
                    ["Streamlit", "code", "Apache 2.0"],
                ],
                (62 * mm, 43 * mm, 60 * mm),
            ),
            Spacer(1, 6),
            Paragraph("6.3 Employment-Related IP Conflicts", H3),
            Paragraph("Is any team member currently bound by an employment, internship, or consulting "
                      "agreement under which their employer could claim ownership of work they create during "
                      "this hackathon? <b>No.</b>", BODY),
        ],
    ),
    (
        "7. DECLARATION",
        [
            Paragraph(
                "By submitting this proposal, the team leader confirms that the information provided is "
                "accurate to the best of the team's knowledge and that the project will be original work "
                "created during the SDC 2026 hackathon period.", BODY),
            Spacer(1, 26),
            Table(
                [
                    ["Signature:", "____________________________________"],
                    ["Name:", LEADER],
                    ["Date:", "______ / ______ / 2026"],
                ],
                colWidths=(32 * mm, 100 * mm),
                style=TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ]
                ),
            ),
        ],
    ),
]


TECH_SECTIONS = [
    (
        "1. TEAM AND PROJECT OVERVIEW",
        [
            kv_table(
                [
                    ("Team Name", TEAM),
                    ("Project / Solution Name", PROJECT),
                    ("Name (Leader)", LEADER),
                    ("Email &amp; Phone (Leader)", f"{EMAIL} / {PHONE}"),
                    ("University Affiliation(s)", UNIVERSITY),
                    ("Live Prototype URL", LIVE),
                    ("Code Repository URL (public)", REPO),
                ]
            )
        ],
    ),
    (
        "2. ARCHITECTURE &amp; TECHNOLOGY STACK",
        [
            Paragraph("2.1 System Architecture Overview", H3),
            Paragraph(
                "The Streamlit user interface is the only client judges and users touch. A user either "
                "uploads a synthetic CV or edits the questionnaire, both of which produce a skill profile "
                "normalised against a fixed vocabulary (feature #1). The UI reads a versioned trend "
                "snapshot from the data store; each record carries its source URL and retrieval date, and "
                "these are displayed alongside every forecast (feature #2). The matching and pathway engine "
                "consumes the profile plus the snapshot and returns ranked roles with a four-component "
                "explainable score, the exact skill gap (feature #3), an ordered reskilling plan (feature "
                "#4), SDG tags on every role (feature #5) and a moderate-versus-fast scenario comparison "
                "(feature #6). CV parsing and scoring run locally in the app with no external AI service, with a "
                "local rule-based fallback so the demo degrades gracefully. A scheduled ingestion job "
                "refreshes trend snapshots from public sources. See the appended block diagram.", BODY),
            Spacer(1, 4),
            Paragraph("2.2 Languages, Frameworks &amp; Libraries", H3),
            grid_table(
                ["Name &amp; Version", "Purpose in Project", "License"],
                [
                    ["Python 3.11+", "Application and engine language", "PSF"],
                    ["Streamlit 1.66", "Web UI, file upload, tables", "Apache 2.0"],
                    ["pandas 2.x", "Tabular handling", "BSD 3-Clause"],
                    ["reportlab", "Build these submission PDFs (offline tool)", "BSD"],
                    ["None (no ML library loaded at runtime)", "All scoring is a deterministic rule set", "Apache 2.0"],
                    ["unittest (stdlib)", "Unit tests for the scoring engine", "PSF"],
                ],
                (52 * mm, 68 * mm, 45 * mm),
            ),
        ],
    ),
    (
        "3. APIs &amp; CLOUD SERVICES",
        [
            Paragraph("3.1 External APIs", H3),
            grid_table(
                ["API and Provider", "Purpose in Project", "Access Tier"],
                [
                    ["None — no external AI API is called", "CV parsing and scoring run locally in the app", "—"],
                    ["WEF / O*NET / HRD Corp public data feeds", "Trend snapshot ingestion (public data)", "free"],
                    ["Streamlit Community Cloud", "Hosting the public live demo", "free"],
                    ["—", "—", "—"],
                ],
                (62 * mm, 68 * mm, 35 * mm),
            ),
            Spacer(1, 4),
            Paragraph("No API keys or secrets are included in this document.", NOTE),
            Spacer(1, 4),
            Paragraph("3.2 Cloud Platforms &amp; Deployment", H3),
            grid_table(
                ["Service &amp; Provider", "Purpose in Project", "Plan / Region"],
                [
                    ["Streamlit Community Cloud", "Public live demo (auto-deploy from GitHub main)", "Community / global"],
                    ["Replit", "Development workspace and alternative hosting", "Free tier"],
                    ["Streamlit Community Cloud", "Auto-deploy from GitHub main on every push", "Community / global"],
                    ["GitHub (douyinlin)", "Source control and deployment trigger", "Free"],
                ],
                (52 * mm, 68 * mm, 45 * mm),
            ),
        ],
    ),
    (
        "4. AI TOOLS, MODELS &amp; DATASETS",
        [
            Paragraph("4.1 AI Models Used in the Solution", H3),
            grid_table(
                ["Model &amp; Version", "Source / Provider", "Usage", "License / Terms"],
                [
                    ["No pre-trained model is loaded at runtime", "—", "—", "—"],
                    ["Rule-based skill extractor (in-house)", "Team-built", "rules only", "Apache 2.0"],
                    ["Dictionary-matched taxonomy (O*NET / ESCO inspired)", "Team-curated", "catalogue", "CC BY 4.0 (O*NET)"],
                ],
                (48 * mm, 42 * mm, 32 * mm, 43 * mm),
            ),
            Spacer(1, 4),
            Paragraph("4.2 Datasets", H3),
            grid_table(
                ["Dataset", "Source / URL", "Type", "License", "Personal data?"],
                [
                    ["O*NET skills & occupations", "onetcenter.org", "public", "CC BY 4.0", "No"],
                    ["WEF Future of Jobs indicators", "weforum.org", "public", "Cited", "No"],
                    ["HRD Corp course directory", "hrdcorp.gov.my", "public", "Public directory", "No"],
                    ["Demo profiles & sample CV", "Team-authored", "synthetic", "Apache 2.0", "No"],
                ],
                (40 * mm, 40 * mm, 22 * mm, 30 * mm, 33 * mm),
            ),
            Spacer(1, 4),
            Paragraph("4.3 AI-Assisted Development Tools", H3),
            Paragraph("Did your team use any generative-AI tool to help create code, design, text, or other "
                      "project material? <b>Yes</b>.", BODY),
            grid_table(
                ["Tool &amp; Version", "Used For", "Extent of Use"],
                [
                    ["DeepSeek-based coding assistant", "Scaffolding, boilerplate, documentation drafting", "moderate"],
                    ["GitHub Copilot", "Inline code completion", "minor"],
                ],
                (55 * mm, 70 * mm, 40 * mm),
            ),
            Spacer(1, 6),
            Paragraph(
                "Review statement: Every AI-generated block was read, tested or rewritten by a team member; "
                "matching logic, SDG tags and all statistics are hand-verified against the cited sources. "
                "Unit tests cover the scoring and pathway functions, and a reviewer other than the author "
                "checks each pull request before merge.", BODY),
        ],
    ),
    (
        "5. SPONSOR-PROVIDED RESOURCES",
        [
            Paragraph("Did your project use any official SDC sponsor-provided resource? <b>Yes</b>.", BODY),
            grid_table(
                ["Sponsor", "Resource", "How It Was Used in the Project"],
                [
                    ["SDC 2026 programme", "Replit workspace",
                     "Development environment for the prototype during the build phase"],
                    ["None", "No RunPod endpoint is used",
                     "CV parsing runs locally; the app makes no GPU or external AI call"],
                ],
                (45 * mm, 45 * mm, 75 * mm),
            ),
            Spacer(1, 6),
            Paragraph("Essentiality: The Replit workspace removed local setup so all five members could work on the same running prototype, and the public demo is hosted on Streamlit Community Cloud. Neither is essential to the logic: the app runs on any Python host with no external AI service, so the solution survives if workspace access ends.", BODY),
        ],
    ),
    (
        "6. SECURITY, PRIVACY &amp; RESPONSIBLE USE",
        [
            Paragraph("6.1 Data Handling &amp; Privacy", H3),
            Paragraph(
                "The public demo processes no real personal data. Users either pick a synthetic sample "
                "profile or upload a synthetic CV that the team authored; the interface states this rule "
                "next to the upload widget. Uploaded text is parsed in memory to extract skill names and is "
                "never written to disk, logged or stored in a database. No account, login or cookie is used "
                "beyond the Streamlit session itself. API keys live in platform secrets (Replit Secrets / "
                "Streamlit Cloud secrets) and never appear in the repository. If a future version accepts "
                "real CVs, it will require explicit consent, a retention limit and deletion on request.",
                BODY),
            Spacer(1, 4),
            Paragraph("6.2 Known Limitations &amp; Risks", H3),
            Paragraph(
                "Main risks: (1) trend data lag and source bias \u2014 the weights are currently simulated and the "
                "UI labels them as such; (2) rule-based matching can mis-map niche skills \u2014 mitigated by a "
                "curated alias vocabulary and a visible skill-gap breakdown; (3) hallucinated roles or courses "
                "\u2014 impossible by construction, because roles and course links come from a fixed catalogue and "
                "no language model runs at inference time; (4) no GPU acceleration today, so CV parsing is limited "
                "to text-based PDFs and plain text; (5) small pilot size \u2014 statements are labelled as estimates. "
                "The tool supports human career decisions and never makes hiring decisions.", BODY),

        ],
    ),
    (
        "7. COMPLIANCE &amp; READINESS",
        [
            Paragraph(
                "<font color='#8A9A5B'>☑</font> All APIs, cloud services, AI tools, models, and datasets used "
                "in the project are declared in this document.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> All third-party code, datasets, and models are used in "
                "accordance with their licenses, and attribution is provided where required.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> No API keys, passwords, or other credentials are exposed in "
                "the code repository, prototype, or this document.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> Any use of generative-AI tools for development has been "
                "disclosed and reviewed by the team.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> Any use of official SDC sponsor resources has been declared "
                "in Section 5.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> The prototype described here is accessible to judges through "
                "the links provided in Section 1.", BODY),
            Paragraph(
                "<font color='#8A9A5B'>☑</font> All fields in this template have been completed within the "
                "word limits stated.", BODY),
        ],
    ),
    (
        "8. DECLARATION",
        [
            Paragraph(
                "By submitting this document, the team leader confirms that the information provided is "
                "complete and accurate to the best of the team's knowledge, and that every API, cloud "
                "service, AI tool, dataset, model, and sponsor resource used in the project has been "
                "declared.", BODY),
            Spacer(1, 26),
            Table(
                [
                    ["Signature:", "____________________________________"],
                    ["Name:", LEADER],
                    ["Date:", "______ / ______ / 2026"],
                ],
                colWidths=(32 * mm, 100 * mm),
                style=TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ]
                ),
            ),
        ],
    ),
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
        Paragraph("Submission deadline: 25 October 2026", ParagraphStyle(
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


def main() -> None:
    prelim_intro = [
        Paragraph(
            "Phase 1 — Preliminary Project Proposal. Answers below follow the official template order "
            "and the stated word limits (2.1 ≤ 250 words, 2.2 ≤ 300 words, 3.2 ≤ 200 words).", NOTE),
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
            "Technical Tools Declaration. Complete every section; where a category does not apply we "
            "ticked \"No\" or wrote \"None\" rather than leaving it blank.", NOTE),
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
