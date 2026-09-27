"""Registry + config loading helpers."""
from __future__ import annotations

import tomllib
from pathlib import Path

from core.registry import PluginRegistry, PluginSpec
from utils.log import get_logger

log = get_logger(__name__)


def load_registry(path: Path) -> PluginRegistry:
    if not path.exists():
        log.warning("registry %s missing, using defaults", path)
        return PluginRegistry.from_defaults()
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    specs = []
    for entry in raw.get("plugin", []):
        specs.append(
            PluginSpec(
                name=entry["name"],
                module=entry["module"],
                cls=entry["class"],
                version=entry.get("version", "0.0.0"),
                api=entry.get("api", "1"),
                requires=tuple(entry.get("requires", [])),
                enabled=entry.get("enabled", True),
            )
        )
    return PluginRegistry(specs)