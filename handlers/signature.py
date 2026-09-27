"""IDA-style byte signature parsing and scanning."""
from __future__ import annotations

import re
from dataclasses import dataclass

from utils.log import get_logger

log = get_logger(__name__)

_PATTERN_RE = re.compile(r"^[0-9A-Fa-f?][0-9A-Fa-f? ]*$")


@dataclass(frozen=True, slots=True)
class Signature:
    raw: str
    tokens: tuple[int | None, ...]  # None == wildcard

    @property
    def size(self) -> int:
        return len(self.tokens)

    @classmethod
    def parse(cls, raw: str) -> "Signature":
        cleaned = raw.strip()
        if not _PATTERN_RE.match(cleaned):
            raise ValueError(f"invalid signature: {raw!r}")
        tokens: list[int | None] = []
        for tok in cleaned.split():
            if tok in ("?", "??"):
                tokens.append(None)
            elif len(tok) == 2:
                tokens.append(int(tok, 16))
            else:
                raise ValueError(f"bad token {tok!r} in {raw!r}")
        return cls(raw=cleaned, tokens=tuple(tokens))


def scan(buffer: bytes, sig: Signature) -> list[int]:
    """Return offsets in `buffer` where `sig` matches. O(n*m), fine for modules <64MB."""
    hits: list[int] = []
    n, m = len(buffer), sig.size
    if m == 0 or n < m:
        return hits
    first = sig.tokens[0]
    for i in range(n - m + 1):
        if first is not None and buffer[i] != first:
            continue
        for j in range(1, m):
            want = sig.tokens[j]
            if want is not None and buffer[i + j] != want:
                break
        else:
            hits.append(i)
    return hits