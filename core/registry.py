"""Plugin registry: spec storage, dependency resolution, instantiation."""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from utils.log import get_logger

if TYPE_CHECKING:
    from core.contracts import PluginBase

log = get_logger(__name__)


@dataclass(slots=True)
class PluginSpec:
    name: str
    module: str
    cls: str
    version: str = "0.0.0"
    api: str = "1"
    requires: tuple[str, ...] = ()
    enabled: bool = True

    def instantiate(self) -> "PluginBase":
        mod = importlib.import_module(self.module)
        klass = getattr(mod, self.cls)
        return klass()


@dataclass(slots=True)
class PluginRegistry:
    specs: list[PluginSpec] = field(default_factory=list)

    def get(self, name: str) -> PluginSpec:
        for spec in self.specs:
            if spec.name == name:
                return spec
        raise KeyError(name)

    def enabled_specs(self) -> list[PluginSpec]:
        return [s for s in self.specs if s.enabled]

    def resolve_order(self) -> list[str]:
        """Topological sort honoring `requires`. Cycles raise."""
        by_name = {s.name: s for s in self.enabled_specs()}
        visited: set[str] = set()
        order: list[str] = []

        def visit(n: str, stack: tuple[str, ...]) -> None:
            if n in visited:
                return
            if n in stack:
                raise RuntimeError(f"dependency cycle: {' -> '.join((*stack, n))}")
            spec = by_name.get(n)
            if spec is None:
                return
            for dep in spec.requires:
                visit(dep, (*stack, n))
            visited.add(n)
            order.append(n)

        for name in by_name:
            visit(name, ())
        return order

    @classmethod
    def from_defaults(cls) -> "PluginRegistry":
        return cls(
            [
                PluginSpec("schema_reader", "plugins.schema_reader.plugin", "SchemaReader"),
                PluginSpec("netvar_scanner", "plugins.netvar_scanner.plugin", "NetvarScanner"),
                PluginSpec("offset_walker", "plugins.offset_walker.plugin", "OffsetWalker"),
                PluginSpec("sig_scan", "plugins.sig_scan.plugin", "SigScan"),
            ]
        )