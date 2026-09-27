"""Data model for CS2 schema class/field trees."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SchemaField:
    name: str
    type_name: str
    offset: int
    size: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SchemaField":
        return cls(
            name=d["name"],
            type_name=d["type_name"],
            offset=int(d["offset"]),
            size=int(d["size"]),
        )


@dataclass(slots=True)
class SchemaClass:
    name: str
    module: str
    size: int
    fields: list[SchemaField] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SchemaClass":
        return cls(
            name=d["name"],
            module=d["module"],
            size=int(d["size"]),
            fields=[SchemaField.from_dict(f) for f in d.get("fields", [])],
        )

    def field_by_name(self, name: str) -> SchemaField | None:
        for f in self.fields:
            if f.name == name:
                return f
        return None