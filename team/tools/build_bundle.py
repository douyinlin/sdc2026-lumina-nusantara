"""Build one download bundle for the submission folder, plus the deck talking points."""

import zipfile
import argparse
from pathlib import Path

from pptx import Presentation

REPO = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--submission-dir", type=Path, default=REPO / "submission")
parser.add_argument("--output", type=Path, default=REPO / "generated-artifacts/submission/SDC2026_LuminaNusantara_Submission.zip")
args = parser.parse_args()
SUB = args.submission_dir
BUNDLE = args.output
MEMBERS = [
    "SDC2026_LuminaNusantara_Preliminary.pdf",
    "SDC2026_LuminaNusantara_TechDeclaration.pdf",
    "SDC2026_LuminaNusantara_SlideDeck.pptx",
    "REPLIT PROOF OF USE.pdf",
    "README.md",
    "CONTENTS.md",
    "OWNER_ACTIONS.md",
]
missing = [name for name in MEMBERS if not (SUB / name).is_file()]
if missing:
    raise FileNotFoundError(f"Missing authoritative submission originals: {missing}")
BUNDLE.parent.mkdir(parents=True, exist_ok=True)

prs = Presentation(str(SUB / "SDC2026_LuminaNusantara_SlideDeck.pptx"))
lines = [
    "# Deck talking points",
    "",
    "Generated from `submission/SDC2026_LuminaNusantara_SlideDeck.pptx` (12 slides).",
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
(BUNDLE.parent / "DECK_TALKING_POINTS.md").write_text("\n".join(lines), encoding="utf-8")

with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
    for name in MEMBERS:
        path = SUB / name
        z.write(path, arcname=f"submission/{name}")
    z.write(REPO / "README.md", arcname="README.md")
    z.writestr("team/DECK_TALKING_POINTS.md", "\n".join(lines))
    z.write(REPO / "docs/REPLIT_VALIDATION.md", arcname="docs/REPLIT_VALIDATION.md")

print(f"bundle: {BUNDLE.name} | {BUNDLE.stat().st_size / (1024 * 1024):.1f} MB")
