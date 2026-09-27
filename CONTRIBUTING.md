# Contributing to primordial-cs2-dump-toolkit

Thanks for wanting to push the dump pipeline forward. This repo is a plugin host for CS2 offset/schema/netvar extraction — core stays small, everything else is an extension.

## Ground rules

- **Python 3.12+** is the floor. 3.11 works but the async loader path is slower.
- **One plugin, one concern.** If your module does offsets *and* netvars, split it.
- **Contracts are frozen.** `core/contracts.py` is the ABI between host and plugins. Breaking changes require a `MAJOR` bump and a migration note in `CHANGELOG.md`.
- **No silent failures.** Plugins raise `DumpError` subclasses; the host logs and continues unless `--strict` is passed.
- **Tests ship with the code.** A plugin without a fixture in `tests/fixtures/` won't get merged.

## Adding a plugin

1. Drop a package under `plugins/<your_plugin>/`.
2. Implement `PluginBase` from `core/contracts.py`.
3. Register via `entry_points` in `pyproject.toml` OR the local `registry/plugins.toml`.
4. Add a fixture dump under `tests/fixtures/` so CI can run it headless.
5. Run `python -m pytest tests/ -q` and `python -m ruff check .` — both must be green.

## Plugin manifest

```toml
[plugin]
name = "netvar_scanner"
version = "0.4.1"
api = "1"
entry = "plugins.netvar_scanner.plugin:NetvarScanner"
requires = ["schema_reader"]
```

## Style

- `ruff` with the repo config. Line length 100.
- Type hints everywhere. `from __future__ import annotations` at the top.
- Logging via `utils/log.py` — never `print()` outside of CLI entrypoints.
- No global mutable state. The host owns lifecycle.

## Reporting bugs

Open an issue with:
- `python --version`
- CS2 build number (from `steamapps/appmanifest_730.acf`)
- The exact `python -m primordial_dump ...` invocation
- Full traceback and the `logs/last_run.log` tail

## Code of conduct

Be a decent human. Roast the code, not the contributor.