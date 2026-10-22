"""Validated manual import of curated evidence snapshots; no web scraping."""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse

from src.utils import Role

def _signal_strength(sig: dict) -> float:
    """Turn a fixed qualitative weight or a published percentage into a -1..1 signal."""
    if "weight" in sig:
        return float(sig["weight"])
    pct = sig.get("change_pct")
    if pct is None:
        return 0.0
    # +50% or more -> +1.0 ; -50% or worse -> -1.0 ; scaled linearly in between
    return max(-1.0, min(1.0, float(pct) / 50.0))


def apply_trend(roles: list[Role], trend: dict) -> list[Role]:
    """Blend the catalogue trend with the selected source's skill signals.

    Taking the source value alone would give every covered role the same trend
    (+0.7 for any "rising" skill), so the ranking would stop differentiating
    between roles. Half the catalogue baseline keeps them apart; a role the
    source says nothing about keeps its baseline unchanged.
    """
    signals = trend.get("signals") or []
    out = []
    for role in roles:
        relevant = [_signal_strength(s) for s in signals if s["skill"] in (role.required_skills or [])]
        if not relevant:
            out.append(Role(role.name, role.required_skills, role.trend, role.sdg, dict(role.tiers)))
            continue
        delta = sum(relevant) / len(relevant)
        blended = 0.5 * role.trend + 0.5 * delta
        out.append(
            Role(
                role.name,
                role.required_skills,
                max(-1.0, min(1.0, blended)),
                role.sdg,
                dict(role.tiers),
            )
        )
    return out


FILES = {"wef": "wef_future_jobs_2025.json", "jobstreet": "jobstreet_skills_2025.json"}

def validate_snapshot(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Snapshot must be an object")
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
        if row.get("direction") not in {"rising", "stable", "declining"}:
            raise ValueError("Invalid signal direction")
        if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
            raise ValueError("Each signal needs source evidence")
        target = row.get("model_skill") or row["skill"]
        if not isinstance(target, str):
            raise ValueError("Invalid mapped skill")
        target = target.strip().casefold()
        if target in seen:
            raise ValueError("Duplicate target skill")
        seen.add(target)
        if row.get("mapping_kind") == "proxy" and not row.get("mapping_note"):
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
