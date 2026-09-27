"""schema_reader — walks the CS2 schema system and dumps class layouts."""
from __future__ import annotations

from core.contracts import DumpContext, DumpError, DumpResult, PluginBase
from models.schema_node import SchemaClass, SchemaField
from services.dump_writer import write_offsets
from services.s