"""CLI entrypoint for primordial-cs2-dump-toolkit."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from primordial_dump.host import PluginHost
from primordial_dump.loader import load_registry
from utils.log import configure_logging, get_logger

log = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="primordial-dump",
        description="Dump CS2 offsets, schemas, and netvars via the plugin host.",
    )
    p.add_argument("--registry", type=Path, default=Path("registry/plugins.toml"))
    p.add_argument("--config", type=Path, default=Path("config/default.toml"))
    p.add_argument("--out", type=Path, default=Path("dumps"))
    p.add_argument("--only", action="append", default=[], help="Run only these plugin names.")
    p.add_argument("--strict", action="store_true", help="Abort on first plugin error.")
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p


async def _run(args: argparse.Namespace) -> int:
    configure_logging(verbosity=args.verbose)
    registry = load_registry(args.registry)
    host = PluginHost(registry=registry, out_dir=args.out, strict=args.strict)
    await host.start()
    try:
        results = await host.run_all(only=args.only or None)
    finally:
        await host.stop()
    failed = [r.name for r in results if r.error]
    if failed:
        log.warning("plugins failed: %s", ", ".join(failed))
        return 1
    log.info("dumped %d plugin(s) -> %s", len(results), args.out)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        log.warning("interrupted")
        return 130


if __name__ == "__main__":
    sys.exit(main())