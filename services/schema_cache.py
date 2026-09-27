"""On-disk cache for parsed schema layouts keyed by build hash."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from models.schema_node import SchemaClass
from utils.log import get_logger

log = get_logger(__name__)

CACHE_VERSION = 2


class SchemaCache:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, build_hash: str) -> Path:
        return self._root / f"schema.{build_hash[:16]}.v{CACHE_VERSION}.json"

    def load(self, build_hash: str) -> dict[str, SchemaClass] | None:
        path = self._path_for(build_hash)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("cache_version") != CACHE_VERSION:
            log.warning("schema cache version drift, ignoring %s", path)
            return None
        out: dict[str, SchemaClass] = {}
        for name, node in raw["classes"].items():
            out[name] = SchemaClass.from_dict(node)
        log.debug("schema cache hit for %s (%d classes)", build_hash[:12], len(out))
        return out

    def store(self, build_hash: str, classes: dict[str, SchemaClass]) -> Path:
        path = self._path_for(build_hash)
        payload = {
            "cache_version": CACHE_VERSION,
            "build_hash": build_hash,
            "classes": {n: asdict(c) for n, c in classes.items()},
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path