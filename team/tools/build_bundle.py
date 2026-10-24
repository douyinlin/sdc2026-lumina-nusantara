"""Build one download bundle for the submission folder, plus the deck talking points."""

import zipfile
import argparse
import hashlib
import shutil
from urllib.parse import quote
from urllib.request import urlopen
from pathlib import Path

from pptx import Presentation

REPO = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--submission-dir", type=Path, default=REPO / "submission")
parser.add_argument("--fetch-originals", action="store_true",
                    help="Download pinned public originals into ignored generated-artifacts.")
parser.add_argument("--output", type=Path, default=REPO / "generated-artifacts/submission/SDC2026_LuminaNusantara_Submission.zip")
args = parser.parse_args()
SUB = args.submission_dir
if args.fetch_originals:
    SUB = REPO / "generated-artifacts/submission-input"
    SUB.mkdir(parents=True, exist_ok=True)
    originals = {
        "SDC2026_LuminaNusantara_Preliminary.pdf": "892fa3edca17f635b243623e8ccac3d9e218c4e803196119752b7764619ef911",
        "SDC2026_LuminaNusantara_TechDeclaration.pdf": "3e4eff6cf7c103a4dcb2bba1edc5d7cd9e66c8a540b230300b4da446cafe08ae",
        "SDC2026_LuminaNusantara_SlideDeck.pptx": "8889a1512f719a602653b718cd12057f4cb4d5eb4cb4c1e8a918ab945ce98a82",
        "REPLIT PROOF OF USE.pdf": "77cac4face126862a9997d37ce663d462f97cb32adb0583fae2b23df7bbf459b",
    }
    base = "https://raw.githubusercontent.com/douyinlin/sdc2026-lumina-nusantara/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/"
    for name, digest in originals.items():
        with urlopen(base + quote(name), timeout=60) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"Original checksum mismatch: {name}")
        (SUB / name).write_bytes(content)
    for name in ("README.md", "CONTENTS.md", "OWNER_ACTIONS.md"):
        shutil.copyfile(REPO / "submission" / name, SUB / name)
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
    raise FileNotFoundError(f"Missing originals: {missing}. Use --fetch-originals or --submission-dir with the provided originals.")
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
