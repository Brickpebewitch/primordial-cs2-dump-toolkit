"""Netvar table entry model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class NetvarEntry:
    table: str
    prop: str
    offset: int
    type_name: str
    array_len: int = 0

    @property
    def qualified(self) -> str:
        return f"{self.table}::{self.prop}"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NetvarEntry":
        return cls(
            table=d["table"],
            prop=d["prop"],
            offset=int(d["offset"]),
            type_name=d["type_name"],
            array_len=int(d.get("array_len", 0)),
        )