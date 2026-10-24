"""Cue deck for the 4:10-6:00 part of the demo video: what to show, what to say, links."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parents[1]

SAGE = RGBColor(0x6F, 0x81, 0x40)
SAGE_DARK = RGBColor(0x3F, 0x4A, 0x26)
SAGE_PALE = RGBColor(0xF2, 0xF5, 0xE9)
GREY = RGBColor(0x6B, 0x75, 0x60)
INK = RGBColor(0x22, 0x2A, 0x18)
BLUE = RGBColor(0x5B, 0x7F, 0xA6)

REPO = "https://github.com/douyinlin/sdc2026-lumina-nusantara"

SLIDES = [
    {
        "title": "Where the data comes from",
        "show": ["GitHub README, Data sources table",
                 "then data/trends/dosm_q2_2026.json",
                 "stop on source_url, latest_released, extraction_note"],
        "say": ("Three sources, kept separate. DOSM publishes advertised vacancies by occupation - "
                "we transcribe the counts by hand and keep the link, the date and a note on what it "
                "cannot support, inside the JSON itself."),
        "links": [("README data sources", f"{REPO}/blob/main/README.md"),
                  ("dosm_q2_2026.json", f"{REPO}/blob/main/data/trends/dosm_q2_2026.json"),
                  ("wef_future_jobs_2025.json", f"{REPO}/blob/main/data/trends/wef_future_jobs_2025.json")],
        "warn": "Hold 2 seconds on extraction_note - it is the honesty proof.",
    },
    {
        "title": "What the program does, what the AI does",
        "show": ["App results page - point at the score",
                 "then src/utils.py - the scoring function"],
        "say": ("The running application has no model. Parsing is keyword matching, scoring is five "
                "weighted rules in this file, and the pathway is a lookup over a curated catalogue. "
                "Same profile, same answer, every time - and every point is explainable."),
        "links": [("src/utils.py (scoring)", f"{REPO}/blob/main/src/utils.py"),
                  ("src/cv.py (parsing)", f"{REPO}/blob/main/src/cv.py"),
                  ("src/trends.py", f"{REPO}/blob/main/src/trends.py")],
        "warn": "Never say AI scores the user. AI is not on the request path.",
    },
    {
        "title": "Where AI actually helped",
        "show": ["Terminal, already cd'd into the repo",
                 "python -m unittest discover -s tests -p \"test_*.py\"",
                 "let it finish: 54 tests, OK"],
        "say": ("AI tools were used to write this code - DeepSeek, Copilot, Codex. Every change was "
                "read, run and tested before it was kept: that run is 54 automated tests, all passing."),
        "links": [("tests folder", f"{REPO}/tree/main/tests"),
                  ("Technical Declaration 4.3",
                   f"{REPO}/blob/main/submission/SDC2026_LuminaNusantara_TechDeclaration.pdf")],
        "warn": "Clear the terminal first (cls). No personal paths on screen.",
    },
    {
        "title": "Replit and RunPod",
        "show": ["PDF viewer: submission/REPLIT PROOF OF USE.pdf",
                 "scroll one page"],
        "say": ("Replit was our development workspace; the screenshots are in the submission folder. "
                "RunPod is not used - there is no GPU endpoint in this project, and the Technical "
                "Declaration says so."),
        "links": [("Replit proof", f"{REPO}/blob/main/submission/REPLIT%20PROOF%20OF%20USE.pdf"),
                  ("Technical Declaration",
                   f"{REPO}/blob/main/submission/SDC2026_LuminaNusantara_TechDeclaration.pdf")],
        "warn": "Say used / not used in one breath. Do not explain why RunPod is unused.",
    },
    {
        "title": "SDG mapping",
        "show": ["App, scroll to the SDG section",
                 "point at the skill-level tags, not the big icons"],
        "say": ("The track is SDG 4, sub-target 4.4 - skills for employment - with 8.5 as the second "
                "target. The mapping goes down to individual skills, and we label it as our own "
                "reading, not an official UN mapping."),
        "links": [("skills_sdg.json (54 skills)", f"{REPO}/blob/main/data/skills_sdg.json"),
                  ("README, SDG row", f"{REPO}/blob/main/README.md")],
        "warn": "Point at the skill chips. Icon-only is explicitly not enough.",
    },
    {
        "title": "What we tested, honestly",
        "show": ["App: the source-robustness table",
                 "or the terminal still showing the test run"],
        "say": ("What we tested: 54 automated tests, every flow in three languages on synthetic "
                "profiles, and 60 course links checked as reachable. What we have not done: a user "
                "study. Phase 2 targets ten testers, a median plan under five minutes, and 70% "
                "rating a top-three role at least 4 out of 5. Targets, not results."),
        "links": [("courses.json (60 links)", f"{REPO}/blob/main/data/courses.json"),
                  ("sample_cv.txt (synthetic)", f"{REPO}/blob/main/data/sample_cv.txt")],
        "warn": "Keep the last sentence: targets, not results.",
    },
    {
        "title": "Limits and next steps",
        "show": ["README, Known limitations",
                 "or the last slide of the deck"],
        "say": ("Known limits: the occupation-to-skill mapping is our heuristic, one quarter is not a "
                "trend, course fees are unverified, and the parser misses synonyms. Next: verified "
                "course metadata, semantic CV parsing, and the user pilot. Everything planned is "
                "labelled as planned."),
        "links": [("README, limitations", f"{REPO}/blob/main/README.md"),
                  ("Deck, roadmap",
                   f"{REPO}/blob/main/submission/SDC2026_LuminaNusantara_SlideDeck.pptx")],
        "warn": "Close on the product, not on the caveats.",
    },
]


def add_text(slide, left, top, width, height, text, size, bold=False, color=INK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    para = frame.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = "Arial"
    run.font.color.rgb = color
    return box


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

for spec in SLIDES:
    s = prs.slides.add_slide(blank)

    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.22))
    bar.fill.solid()
    bar.fill.fore_color.rgb = SAGE
    bar.line.fill.background()

    add_text(s, Inches(0.6), Inches(0.55), Inches(12.2), Inches(0.9),
             spec["title"], 32, True, SAGE_DARK)

    panel = s.shapes.add_shape(1, Inches(0.6), Inches(1.75), Inches(5.5), Inches(3.25))
    panel.fill.solid()
    panel.fill.fore_color.rgb = SAGE_PALE
    panel.line.color.rgb = RGBColor(0xD8, 0xDF, 0xCA)
    add_text(s, Inches(0.85), Inches(1.92), Inches(5.0), Inches(0.35),
             "ON SCREEN", 11, True, GREY)
    body = s.shapes.add_textbox(Inches(0.85), Inches(2.35), Inches(5.0), Inches(2.5))
    frame = body.text_frame
    frame.word_wrap = True
    for i, line in enumerate(spec["show"]):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        run = para.add_run()
        run.text = "· " + line
        run.font.size = Pt(16)
        run.font.name = "Arial"
        run.font.color.rgb = INK

    say_panel = s.shapes.add_shape(1, Inches(6.45), Inches(1.75), Inches(6.3), Inches(3.25))
    say_panel.fill.solid()
    say_panel.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    say_panel.line.color.rgb = RGBColor(0xB7, 0xC9, 0x8F)
    add_text(s, Inches(6.7), Inches(1.92), Inches(5.8), Inches(0.35),
             "SAY THIS", 11, True, BLUE)
    quote = s.shapes.add_textbox(Inches(6.7), Inches(2.35), Inches(5.8), Inches(2.5))
    qf = quote.text_frame
    qf.word_wrap = True
    qrun = qf.paragraphs[0].add_run()
    qrun.text = "\u201c" + spec["say"] + "\u201d"
    qrun.font.size = Pt(16)
    qrun.font.name = "Arial"
    qrun.font.italic = True
    qrun.font.color.rgb = INK

    add_text(s, Inches(0.6), Inches(5.25), Inches(3.0), Inches(0.3),
             "LINKS", 10, True, GREY)
    link_box = s.shapes.add_textbox(Inches(0.6), Inches(5.55), Inches(8.3), Inches(1.2))
    lf = link_box.text_frame
    lf.word_wrap = True
    for i, (label, url) in enumerate(spec["links"]):
        para = lf.paragraphs[0] if i == 0 else lf.add_paragraph()
        run = para.add_run()
        run.text = label
        run.font.size = Pt(13)
        run.font.name = "Arial"
        run.font.color.rgb = BLUE
        run.hyperlink.address = url

    warn = s.shapes.add_shape(1, Inches(9.15), Inches(5.5), Inches(3.6), Inches(1.15))
    warn.fill.solid()
    warn.fill.fore_color.rgb = RGBColor(0xFB, 0xF4, 0xE4)
    warn.line.color.rgb = RGBColor(0xE6, 0xD3, 0xA8)
    wt = warn.text_frame
    wt.word_wrap = True
    wt.margin_left = Emu(Inches(0.12))
    wr = wt.paragraphs[0].add_run()
    wr.text = spec["warn"]
    wr.font.size = Pt(12)
    wr.font.name = "Arial"
    wr.font.color.rgb = RGBColor(0x7A, 0x5A, 0x1E)

    add_text(s, Inches(0.6), Inches(7.0), Inches(12.2), Inches(0.3),
             "SkillRadar MY · Lumina Nusantara · SDC 2026", 9, False, GREY)

path = OUT / "CUE_DECK_4min10_to_6min.pptx"
prs.save(str(path))
print("saved:", path.name, "| slides:", len(prs.slides))
