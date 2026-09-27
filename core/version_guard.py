"""Guards dumps against running on a mismatched CS2 build."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from core.contracts import VersionMismatch


@dataclass(frozen=True, slots=True)
class BuildRef:
    build_number: int
    module_hash: str
    captured_on: str  # ISO date


def hash_module(path: Path, chunk: int = 1 << 20) -> str:
    """Stream-hash a module (client.dll etc.) without loading it whole."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def assert_build(ref: BuildRef, actual_number: int, actual_hash: str) -> None:
    if ref.build_number != actual_number:
        raise VersionMismatch(
            f"build number {actual_number} != expected {ref.build_number}"
        )
    if ref.module_hash != actual_hash:
        raise VersionMismatch("module hash mismatch — offsets may be stale")