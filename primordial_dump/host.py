"""Plugin host: owns lifecycle, dispatch, and result collection."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path

from core.contracts import DumpContext, DumpError, DumpResult, PluginBase
from core.registry import PluginRegistry
from utils.log import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class HostState:
    started_at: float = field(default_factory=time.monotonic)
    loaded: list[str] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)


class PluginHost:
    """Loads plugins from a registry, runs them against a shared DumpContext."""

    def __init__(self, registry: PluginRegistry, out_dir: Path, strict: bool = False) -> None:
        self._registry = registry
        self._out_dir = out_dir
        self._strict = strict
        self._plugins: dict[str, PluginBase] = {}
        self._state = HostState()
        self._ctx: DumpContext | None = None

    async def start(self) -> None:
        self._out_dir.mkdir(parents=True, exist_ok=True)
        order = self._registry.resolve_order()
        for name in order:
            spec = self._registry.get(name)
            try:
                plugin = spec.instantiate()
            except Exception as exc:  # noqa: BLE001 - plugin load must not kill host
                log.error("failed to load plugin %s: %s", name, exc)
                self._state.errors.append((name, str(exc)))
                if self._strict:
                    raise
                continue
            self._plugins[name] = plugin
            self._state.loaded.append(name)
            log.debug("loaded plugin %s v%s", name, spec.version)
        self._ctx = DumpContext(out_dir=self._out_dir, plugins=tuple(self._plugins))

    async def stop(self) -> None:
        for name, plugin in self._plugins.items():
            try:
                await plugin.teardown()
            except Exception as exc:  # noqa: BLE001
                log.warning("teardown failed for %s: %s", name, exc)

    async def run_all(self, only: list[str] | None = None) -> list[DumpResult]:
        if self._ctx is None:
            raise RuntimeError("host not started")
        targets = only or list(self._plugins)
        results: list[DumpResult] = []
        for name in targets:
            plugin = self._plugins.get(name)
            if plugin is None:
                log.warning("plugin not loaded: %s", name)
                continue
            results.append(await self._run_one(name, plugin))
        return results

    async def _run_one(self, name: str, plugin: PluginBase) -> DumpResult:
        assert self._ctx is not None
        t0 = time.perf_counter()
        try:
            result = await asyncio.wait_for(
                plugin.dump(self._ctx), timeout=plugin.timeout_s
            )
        except asyncio.TimeoutError:
            log.error("plugin %s timed out after %.1fs", name, plugin.timeout_s)
            result = DumpResult(name=name, error=f"timeout after {plugin.timeout_s}s")
        except DumpError as exc:
            log.error("plugin %s failed: %s", name, exc)
            result = DumpResult(name=name, error=str(exc))
        except Exception as exc:  # noqa: BLE001
            log.exception("plugin %s crashed", name)
            result = DumpResult(name=name, error=f"unhandled: {exc}")
        result.duration_ms = (time.perf_counter() - t0) * 1000.0
        if result.error and self._strict:
            raise DumpError(f"strict mode: plugin {name} failed")
        return result