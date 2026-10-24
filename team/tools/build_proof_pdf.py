from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "team" / "proof"
OUT = ROOT / "submission" / "REPLIT PROOF OF USE.pdf"

OLIVE = colors.HexColor("#8A9A5B")
DARK = colors.HexColor("#333333")

W, H = landscape(A4)
M = 13 * mm

PAGES = [
    ("replit-running.png", "1 — The application running inside Replit",
     "SkillRadar MY is open in the Replit workspace and serving its three entry points "
     "(jobseeker, HR / L&D, career centre / TVET). The address bar shows the project URL "
     "replit.com/@duyulin18/SkillRadar-MY-Streamlit-app."),
    ("replit-files.png", "2 — The project files inside Replit",
     "The complete source is present in the Repl: app.py (Streamlit entry point), src/i18n.py and "
     "src/utils.py (scoring engine), data/roles.json and team/archive/derived_latest_q2_2025.json, plus "
     "requirements.txt. This is the code that runs the public demo."),
    ("replit-git.png", "3 — Version history inside Replit",
     "Work on the prototype is tracked by Replit's own version control, with a commit history from "
     "the first scaffold through to the current implementation."),
]

ss = getSampleStyleSheet()
H_STYLE = ParagraphStyle("H", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=16,
                         leading=19, textColor=DARK, spaceAfter=1)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica", fontSize=9,
                     leading=12, textColor=colors.HexColor("#5f6b52"))
CAP = ParagraphStyle("CAP", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=10,
                     leading=12.5, textColor=OLIVE, spaceBefore=1, spaceAfter=1)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica", fontSize=8.2,
                      leading=10.5, textColor=DARK)


def wrap(text, style, width):
    from reportlab.platypus import Paragraph, Frame
    p = Paragraph(text, style)
    w, h = p.wrapOn(None, width, 1000)
    return p, h


def build():
    c = pdfcanvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("SDC2026 Lumina Nusantara - Replit Proof of Use")
    c.setAuthor("Lumina Nusantara / DU YULIN")

    total = len(PAGES)
    for idx, (fname, caption, note) in enumerate(PAGES, start=1):
        path = PROOF / fname
        y = H - M

        # ---- header (only on first page)
        if idx == 1:
            h_para, hh = wrap("Replit Proof of Use", H_STYLE, W - 2 * M)
            h_para.drawOn(c, M, y - hh)
            y -= hh + 2

            sub_txt = ("SDC Hackathon 2026 · Domain 1 · Team <b>Lumina Nusantara</b> · "
                       "Leader <b>DU YULIN</b> · Project <b>SkillRadar MY</b><br/>"
                       "Replit account: <b>@duyulin18</b> · Repl: <b>SkillRadar-MY-Streamlit-app</b>")
            s_para, sh = wrap(sub_txt, SUB, W - 2 * M)
            s_para.drawOn(c, M, y - sh)
            y -= sh + 6

            c.setFillColor(OLIVE)
            c.rect(M, y, W - 2 * M, 1.4, stroke=0, fill=1)
            y -= 8
        else:
            y -= 4

        cap_para, ch = wrap(caption, CAP, W - 2 * M)
        cap_para.drawOn(c, M, y - ch)
        y -= ch + 2

        body_para, bh = wrap(note, BODY, W - 2 * M)
        body_para.drawOn(c, M, y - bh)
        y -= bh + 6

        # ---- image scaled into remaining space
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        avail_h = y - (M + 10)
        avail_w = W - 2 * M
        scale = min(avail_w / iw, avail_h / ih)
        dw, dh = iw * scale, ih * scale
        x = M + (avail_w - dw) / 2

        c.setStrokeColor(colors.HexColor("#BBBBBB"))
        c.setLineWidth(0.6)
        c.rect(x - 1.5, y - dh - 1.5, dw + 3, dh + 3, stroke=1, fill=0)
        c.drawImage(str(path), x, y - dh, width=dw, height=dh)

        # ---- footer
        c.setFont("Helvetica", 7.2)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(M, 7 * mm, "Lumina Nusantara  ·  SDC 2026  ·  Domain 1  ·  Replit Proof of Use")
        c.drawRightString(W - M, 7 * mm, f"Page {idx} / {total}")

        c.showPage()

    c.save()
    print("wrote", OUT, "pages:", total)


build()
