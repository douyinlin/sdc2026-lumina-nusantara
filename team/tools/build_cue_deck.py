"""Cue deck for the 4:10-6:00 part of the demo video: one title and its links per slide."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parents[1]

SAGE = RGBColor(0x6F, 0x81, 0x40)
SAGE_DARK = RGBColor(0x3F, 0x4A, 0x26)
GREY = RGBColor(0x6B, 0x75, 0x60)
BLUE = RGBColor(0x2F, 0x5B, 0x8A)

REPO = "https://github.com/douyinlin/sdc2026-lumina-nusantara"

SLIDES = [
    ("Where the data comes from", [
        ("Data sources explained", f"{REPO}/blob/main/docs/DATA.md"),
    ]),
    ("What the program does, what the AI does", [
        ("How the score is built", f"{REPO}/blob/main/docs/TECH.md"),
    ]),
    ("Where AI actually helped", [
        ("Technical Declaration, signed",
         f"{REPO}/blob/main/submission/SDC2026_LuminaNusantara_TechDeclaration.pdf"),
    ]),
    ("Replit and RunPod", [
        ("Replit proof of use", f"{REPO}/blob/main/submission/REPLIT%20PROOF%20OF%20USE.pdf"),
    ]),
    ("SDG mapping", [
        ("SDG mapping and why 4.4", f"{REPO}/blob/main/docs/SDG.md"),
    ]),
    ("What we tested, honestly", [
        ("The course catalogue", f"{REPO}/blob/main/docs/COURSES.md"),
    ]),
    ("Limits and next steps", [
        ("What was tested, what was not", f"{REPO}/blob/main/docs/VALIDATION.md"),
    ]),
]

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

for title, links in SLIDES:
    s = prs.slides.add_slide(blank)

    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.2))
    bar.fill.solid()
    bar.fill.fore_color.rgb = SAGE
    bar.line.fill.background()

    head = s.shapes.add_textbox(Inches(0.7), Inches(0.75), Inches(12.0), Inches(1.2))
    hf = head.text_frame
    hf.word_wrap = True
    hr = hf.paragraphs[0].add_run()
    hr.text = title
    hr.font.size = Pt(38)
    hr.font.bold = True
    hr.font.name = "Arial"
    hr.font.color.rgb = SAGE_DARK

    box = s.shapes.add_textbox(Inches(0.75), Inches(2.45), Inches(11.8), Inches(3.2))
    frame = box.text_frame
    frame.word_wrap = True
    for i, (label, url) in enumerate(links):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.space_after = Pt(18)
        run = para.add_run()
        run.text = label
        run.font.size = Pt(24)
        run.font.name = "Arial"
        run.font.color.rgb = BLUE
        run.font.underline = True
        run.hyperlink.address = url

    foot = s.shapes.add_textbox(Inches(0.75), Inches(6.95), Inches(11.8), Inches(0.35))
    fr = foot.text_frame.paragraphs[0].add_run()
    fr.text = "SkillRadar MY · Lumina Nusantara · SDC 2026"
    fr.font.size = Pt(10)
    fr.font.name = "Arial"
    fr.font.color.rgb = GREY

path = OUT / "CUE_DECK_4min10_to_6min.pptx"
prs.save(str(path))
print("saved:", path.name, "| slides:", len(prs.slides))
