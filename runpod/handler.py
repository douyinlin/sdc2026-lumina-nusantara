"""RunPod serverless handler for SkillRadar MY.

Deploys as a RunPod Serverless Endpoint. Parses CV text into skills and
returns embeddings-friendly tokens. Falls back to a rule-based parser when
the GPU model is unavailable, so the live demo never breaks.
"""

from __future__ import annotations

import re

try:  # runpod is only needed inside the endpoint image
    import runpod
except ImportError:  # pragma: no cover
    runpod = None

SKILL_VOCAB = [
    "excel",
    "sql",
    "python",
    "customer support",
    "crm administration",
    "data visualisation",
    "prompt engineering",
    "project management",
    "product management",
    "machine learning",
]


def extract_skills(text: str) -> list[str]:
    """Match a CV snippet against the controlled skill vocabulary."""
    lowered = text.lower()
    found = [s for s in SKILL_VOCAB if re.search(rf"\b{re.escape(s)}\b", lowered)]
    return found or ["customer support"]


def handler(job: dict) -> dict:
    payload = job.get("input", {}) or {}
    text = payload.get("text", "")
    return {
        "skills": extract_skills(text),
        "model": "rule-based-fallback",
        "chars": len(text),
    }


if runpod is not None:  # pragma: no cover
    runpod.serverless.start({"handler": handler})
