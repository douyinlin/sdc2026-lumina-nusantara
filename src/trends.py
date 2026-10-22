"""Validated manual import of curated evidence snapshots; no web scraping."""
from __future__ import annotations
import argparse
import copy
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse

from src.utils import Role, normalize_skills

def _signal_strength(sig: dict) -> float:
    """Turn a fixed qualitative weight or a published percentage into a -1..1 signal."""
    if "weight" in sig:
        return float(sig["weight"])
    pct = sig.get("change_pct")
    if pct is None:
        return 0.0
    # +50% or more -> +1.0 ; -50% or worse -> -1.0 ; scaled linearly in between
    return max(-1.0, min(1.0, float(pct) / 50.0))


def normalize_match_key(value: object) -> str:
    """Use the scoring taxonomy normalization, while rejecting empty keys."""
    if not isinstance(value, str):
        raise ValueError("A match key must be text")
    keys = normalize_skills([value])
    if not keys:
        raise ValueError("A match key must not be blank")
    return keys[0]


def signal_key(signal: dict) -> str | None:
    """None explicitly marks context-only evidence; support old internal signals."""
    if "match_key" in signal:
        value = signal["match_key"]
        return None if value is None else normalize_match_key(value)
    return normalize_match_key(signal.get("skill"))


def snapshot_signals(snapshot: dict, weight: float = 0.7) -> list[dict]:
    """Keep source skill/model_skill text intact and add a separate scoring key."""
    data = validate_snapshot(snapshot)
    return [{**row, "weight": {"rising": weight, "declining": -weight, "stable": 0.0}[row["direction"]]}
            for row in data["skill_signals"]]


def apply_trend(roles: list[Role], trend: dict) -> list[Role]:
    """Blend matched signals with role baselines; context-only rows never score."""
    signals = trend.get("signals") or []
    indexed: dict[str, float] = {}
    for signal in signals:
        key = signal_key(signal)
        if key is None:
            continue
        if key in indexed:
            raise ValueError("Duplicate normalized trend match key: " + key)
        indexed[key] = _signal_strength(signal)
    out = []
    for role in roles:
        required = normalize_skills(role.required_skills)
        relevant = [indexed[key] for key in required if key in indexed]
        blended = 0.5 * role.trend + 0.5 * sum(relevant) / len(relevant) if relevant else role.trend
        out.append(Role(role.name, role.required_skills, max(-1.0, min(1.0, blended)), role.sdg, dict(role.tiers)))
    return out


FILES = {"wef": "wef_future_jobs_2025.json", "jobstreet": "jobstreet_skills_2025.json"}

def validate_snapshot(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Snapshot must be an object")
    data = copy.deepcopy(data)
    for key in ("source", "source_url", "published", "retrieved_at", "extraction_note"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError("Missing metadata: " + key)
    url = urlparse(data["source_url"])
    if url.scheme != "https" or not url.netloc:
        raise ValueError("Source URL must be HTTPS")
    for key in ("published", "retrieved_at"):
        date.fromisoformat(data[key])
    if data["published"] > data["retrieved_at"]:
        raise ValueError("Retrieval cannot precede publication")
    rows = data.get("skill_signals")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Non-empty skill_signals required")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("skill"), str) or not row["skill"].strip():
            raise ValueError("Each signal needs a skill")
        if not isinstance(row.get("direction"), str) or row["direction"] not in {"rising", "stable", "declining"}:
            raise ValueError("Invalid signal direction")
        if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
            raise ValueError("Each signal needs source evidence")
        # Preserve source wording. Only match_key is canonicalized.
        kind = row.get("mapping_kind")
        if kind is not None and kind not in ("proxy", "aligned", "unmapped"):
            raise ValueError("Invalid mapping kind")
        if "model_skill" in row:
            target = normalize_match_key(row["model_skill"])
            if kind == "unmapped":
                raise ValueError("Context-only evidence cannot have a model_skill")
        elif kind == "unmapped":
            target = None
        else:
            target = normalize_match_key(row["skill"])
        if target is not None:
            if target in seen:
                raise ValueError("Duplicate normalized target skill")
            seen.add(target)
        row["match_key"] = target
        if kind == "proxy" and (not isinstance(row.get("mapping_note"), str) or not row["mapping_note"].strip()):
            raise ValueError("Proxy mappings require an explanation")
    return data

def read_snapshot(path: Path) -> dict:
    return validate_snapshot(json.loads(path.read_text(encoding="utf-8")))

def _atomic_json(path: Path, value: dict) -> None:
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def update_status(folder: Path, kind: str) -> dict:
    path = folder / ("." + kind + "-import-status.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {"ok": False}

def import_snapshot(kind: str, incoming: Path, folder: Path) -> None:
    if kind not in FILES:
        raise ValueError("Unknown source")
    status = {"attempted_at": datetime.now(timezone.utc).isoformat(), "method": "manual reviewed JSON import"}
    try:
        data = read_snapshot(incoming)
        expected_host = "www.weforum.org" if kind == "wef" else "theedgemalaysia.com"
        if urlparse(data["source_url"]).hostname != expected_host:
            raise ValueError("Source URL does not match selected source")
        target = folder / FILES[kind]
        if target.exists():
            try:
                previous = read_snapshot(target)
            except (ValueError, OSError):
                previous = None  # Do not replace a good backup with a corrupt file.
            if previous is not None:
                _atomic_json(target.with_suffix(".json.bak"), previous)
        _atomic_json(target, data)
    except (ValueError, OSError, TypeError) as exc:
        _atomic_json(folder / ("." + kind + "-import-status.json"), {**status, "ok": False, "error_type": type(exc).__name__})
        raise
    _atomic_json(folder / ("." + kind + "-import-status.json"), {**status, "ok": True, "source_url": data["source_url"], "published": data["published"], "retrieved_at": data["retrieved_at"]})

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=FILES)
    parser.add_argument("input", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    args = parser.parse_args()
    try:
        if args.check:
            read_snapshot(args.input)
        else:
            import_snapshot(args.source, args.input, Path(__file__).resolve().parents[1] / "data" / "trends")
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(1, "Import rejected; existing snapshot preserved: " + str(exc) + "\n")
    print("Validation passed" if args.check else "Snapshot imported; review git diff before committing")

if __name__ == "__main__":
    main()
