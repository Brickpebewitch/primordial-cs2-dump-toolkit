"""Attach to a running cs2.exe and expose a read-only memory view."""
from __future__ import annotations

from dataclasses import dataclass

from core.contracts import DumpError
from utils.log import get_logger

log = get_logger(__name__)

TARGET_PROCESS = "cs2.exe"


@dataclass(slots=True)
class ProcessHandle:
    pid: int
    base: int
    module_size: int

    def read(self, addr: int, size: int) -> bytes:
        raise NotImplementedError("concrete backend provides read()")


class PymemBackend(ProcessHandle):
    """Thin wrapper over pymem. Kept read-only by contract."""

    def __init__(self, pid: int, base: int, module_size: int, pm: object) -> None:
        super().__init__(pid=pid, base=base, module_size=module_size)
        self._pm = pm

    def read(self, addr: int, size: int) -> bytes:
        try:
            return self._pm.read_bytes(addr, size)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            raise DumpError(f"read failed at 0x{addr:x} (+{size})") from exc


def attach(name: str = TARGET_PROCESS) -> ProcessHandle:
    try:
        import pymem  # noqa: PLC0415
    except ImportError as exc:
        raise DumpError("pymem not installed — pip install pymem") from exc
    try:
        pm = pymem.Pymem(name)
    except Exception as exc:  # noqa: BLE001
        raise DumpError(f"could not attach to {name}: {exc}") from exc
    mod = pymem.process.module_from_name(pm.process_handle, name)
    base = mod.lpBaseOfDll
    size = mod.SizeOfImage
    log.info("attached to %s pid=%d base=0x%x size=0x%x", name, pm.process_id, base, size)
    return PymemBackend(pid=pm.process_id, base=base, module_size=size, pm=pm)