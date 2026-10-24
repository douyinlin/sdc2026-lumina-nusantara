"""Build one download bundle for the submission folder, plus the deck talking points."""

import zipfile
from pathlib import Path

from pptx import Presentation

REPO = Path(__file__).resolve().parents[2]
SUB = REPO / "submission"

prs = Presentation(str(SUB / "SDC2026_LuminaNusantara_SlideDeck.pptx"))
lines = [
    "# Deck talking points",
    "",
    f"Generated from `submission/SDC2026_LuminaNusantara_SlideDeck.pptx` ({len(prs.slides)} slides).",
    "Each slide lists its own text, top to bottom.",
    "",
]
for i, slide in enumerate(prs.slides, 1):
    lines.append(f"## Slide {i}")
    lines.append("")
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = " ".join(shape.text_frame.text.split())
        if text:
            lines.append(f"- {text}")
    if not any(shape.has_text_frame and shape.text_frame.text.strip() for shape in slide.shapes):
        lines.append("- (image or chart only)")
    lines.append("")
(REPO / "team" / "DECK_TALKING_POINTS.md").write_text("\n".join(lines), encoding="utf-8")

BUNDLE = SUB / "SDC2026_LuminaNusantara_Submission.zip"
MEMBERS = [
    "SDC2026_LuminaNusantara_Preliminary.pdf",
    "SDC2026_LuminaNusantara_TechDeclaration.pdf",
    "SDC2026_LuminaNusantara_SlideDeck.pptx",
    "REPLIT PROOF OF USE.pdf",
    "README.md",
]
with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
    for name in MEMBERS:
        path = SUB / name
        if path.exists():
            z.write(path, arcname=name)
        else:
            print("missing:", name)

print(f"bundle: {BUNDLE.name} | {BUNDLE.stat().st_size / (1024 * 1024):.1f} MB")
