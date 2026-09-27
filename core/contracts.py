"""Frozen ABI between the host and plugins. Bump MAJOR on break."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

API_VERSION = "1"


class DumpError(RuntimeError):
    """Raised by plugins for recoverable failures."""


class VersionMismatch(DumpError):
    """Raised when the target CS2 build hash doesn't match the guard."""


@dataclass(slots=True)
class DumpContext:
    out_dir: Path
    plugins: tuple[Any, ...] = ()
    config: dict[str, Any] = field(default_factory=dict)
    proc_handle: Any | None = None


@dataclass(slots=True)
class DumpResult:
    name: str
    artifacts: list[Path] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0


class PluginBase(ABC):
    """Every plugin implements this. Host owns lifecycle and I/O."""

    name: ClassVar[str] = "unnamed"
    version: ClassVar[str] = "0.0.0"
    api: ClassVar[str] = API_VERSION
    timeout_s: ClassVar[float] = 30.0

    @abstractmethod
    async def dump(self, ctx: DumpContext) -> DumpResult:
        """Produce artifacts into ctx.out_dir. Must not block the loop."""

    async def teardown(self) -> None:  # noqa: B027 - optional hook
        return None