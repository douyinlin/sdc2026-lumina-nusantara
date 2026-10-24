"""Text-based CV skill extraction for synthetic demos; scanned PDFs need OCR."""
import io
import json
from pathlib import Path
import re
import zlib

ALIASES = {
    "customer service": "customer support", "helpdesk": "customer support",
    "zendesk": "crm administration", "salesforce": "crm administration",
    "crm": "crm administration", "power bi": "data visualisation",
    "tableau": "data visualisation", "dashboard": "data visualisation",
    "chatgpt": "prompt engineering", "genai": "prompt engineering",
    "generative ai": "prompt engineering", "llm": "prompt engineering",
    "spreadsheet": "excel", "pandas": "python", "pytorch": "machine learning",
    "tensorflow": "machine learning", "agile": "project management",
    "scrum": "project management", "pmp": "project management",
    "supervisor": "team lead", "manager": "team lead",
    "stakeholder": "stakeholder management", "presentation": "presentation",
    "rpa": "automation", "automation": "automation",
    "process improvement": "process improvement",
    "communication": "communication",
}


def _extract_pdf_text(raw: bytes) -> str:
    """Use pypdf for standard PDF text/font decoding, then the legacy fallback."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw), strict=False)
        if reader.is_encrypted:
            reader.decrypt("")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        # Malformed, encrypted, or otherwise unsupported files may still be
        # readable by the narrow fallback below.
        pass

    chunks = []
    for match in re.finditer(rb"stream\r?\n", raw):
        start, end = match.end(), raw.find(b"endstream", match.end())
        if end == -1:
            continue
        try:
            blob = zlib.decompress(raw[start:end])
        except Exception:
            continue
        chunks += [
            token.group(1).decode("latin-1", "ignore")
            for token in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)\s*Tj", blob)
        ]
        for array in re.finditer(rb"\[(.*?)\]\s*TJ", blob, re.S):
            chunks += [
                token.group(1).decode("latin-1", "ignore")
                for token in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)", array.group(1))
            ]
    return " ".join(chunks)


def cv_to_skills(uploaded) -> list[str]:
    raw = uploaded.read()
    name = (getattr(uploaded, "name", "") or "").lower()
    text = _extract_pdf_text(raw) if name.endswith(".pdf") else raw.decode("utf-8", "ignore")

    low = text.casefold()
    found: list[str] = []
    catalogue = json.loads(
        (Path(__file__).resolve().parents[1] / "data" / "roles.json").read_text(encoding="utf-8")
    )
    names = {
        item if isinstance(item, str) else item["skill"]
        for role in catalogue["roles"]
        for item in role["skills"]
    }
    aliases = {**{key: key for key in sorted(names)}, **ALIASES}
    for alias, key in aliases.items():
        if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", low) and key not in found:
            found.append(key)
    return found
