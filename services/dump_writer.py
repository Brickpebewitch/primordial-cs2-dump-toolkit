"""Serializes dump artifacts to disk in stable, diff-friendly formats."""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from utils.log import get_logger

log = get_logger(__name__)


def write_offsets(out_dir: Path, name: str, offsets: Mapping[str, int]) -> Path:
    """Offsets are written as hex strings so diffs don't churn on decimal noise."""
    path = out_dir / f"{name}.offsets.json"
    payload = {
        "schema": "primordial.offsets/1",
        "count": len(offsets),
        "offsets": {k: f"0x{v:x}" for k, v in sorted(offsets.items())},
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    log.info("wrote %d offsets -> %s", len(offsets), path)
    return path


def write_netvars(out_dir: Path, name: str, netvars: Sequence[tuple[str, int, str]]) -> Path:
    """netvars: (table, prop_offset, type_name) tuples."""
    path = out_dir / f"{name}.netvars.json"
    payload = {
        "schema": "primordial.netvars/1",
        "count": len(netvars),
        "entries": [
            {"table": t, "offset": f"0x{o:x}", "type": ty} for t, o, ty in netvars
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    log.info("wrote %d netvars -> %s", len(netvars), path)
    return path