"""Read-only memory helpers. No writes, ever."""
from __future__ import annotations

import struct

from core.contracts import DumpError
from handlers.process_attach import ProcessHandle


def read_u32(handle: ProcessHandle, addr: int) -> int:
    return struct.unpack("<I", handle.read(addr, 4))[0]


def read_u64(handle: ProcessHandle, addr: int) -> int:
    return struct.unpack("<Q", handle.read(addr, 8))[0]


def read_cstring(handle: ProcessHandle, addr: int, max_len: int = 256) -> str:
    """Read a NUL-terminated string. Caps at max_len to avoid runaway walks."""
    buf = bytearray()
    cursor = addr
    while len(buf) < max_len:
        chunk = handle.read(cursor, 16)
        nul = chunk.find(b"\x00")
        if nul != -1:
            buf.extend(chunk[:nul])
            return buf.decode("utf-8", errors="replace")
        buf.extend(chunk)
        cursor += 16
    raise DumpError(f"cstring at 0x{addr:x} exceeded {max_len} bytes")