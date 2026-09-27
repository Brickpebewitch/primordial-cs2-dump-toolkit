# Security Policy

## Scope

`primordial-cs2-dump-toolkit` reads process memory from a running CS2 client
for the purpose of extracting offsets, schema layouts, and netvar tables. It
does **not** write to the target process, does **not** inject DLLs, and does
**not** ship any bypass for anti-cheat. If a plugin in this repo does any of
those things, that's a bug and we want to know.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅ |
| 0.5.x   | ⚠️ security fixes only |
| < 0.5   | ❌ |

## Reporting a vulnerability

Do **not** open a public issue for memory-safety or privilege-escalation bugs.

- Email: `security@primordial-dump.dev` (PGP key in `docs/pgp.asc`)
- Or use GitHub private vulnerability reporting on this repo.

Include:
- Affected file + function
- A minimal reproduction (fixture dump if possible)
- Whether it requires elevated privileges to trigger

We aim to acknowledge within 72h and ship a patch within 14 days for
confirmed issues. Credit in the advisory unless you ask otherwise.

## Out of scope

- Detections by Valve / VAC. That's a cat-and-mouse game, not a vuln.
- "My account got banned." Reading memory is against the CS2 ToS. You knew.
- Plugins that live outside this repo. Report those to their maintainers.

## For contributors

- Never commit a real CS2 process dump. Fixtures must be synthetic or
  heavily redacted.
- Never commit offsets tied to a specific live build without a
  `build_hash` guard. See `core/version_guard.py`.