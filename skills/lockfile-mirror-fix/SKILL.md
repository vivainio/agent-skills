---
name: lockfile-mirror-fix
description: Replace internal registry mirror URLs in package-lock.json/uv.lock with public npm/pypi URLs. Needed to fix CI failures where the CI runner can't reach internal PyPI/npm mirrors baked into the lockfile. Never activates automatically — only engages after explicit `/lockfile-mirror-fix` invocation.
disable-model-invocation: true
---

# lockfile-mirror-fix

Fixes CI failures caused by lockfiles pointing at an internal registry
mirror (e.g. a corporate npm/PyPI proxy) that the CI runner can't reach —
symptoms include `ENOTFOUND`/DNS or connection-refused errors during
`npm ci`/`uv sync` against a mirror hostname. Rewriting the URLs to the
public npm/PyPI registries fixes it.

Run the matching script from the directory containing the lockfile. Each
detects the mirror host from the file itself — nothing to fill in.

**package-lock.json**: `python ~/.claude/skills/lockfile-mirror-fix/scripts/fix_npm.py`

**uv.lock**: `python ~/.claude/skills/lockfile-mirror-fix/scripts/fix_uv.py`

Run the uv one last — a later `uv sync`/`uv lock`/`uv add` will re-clobber
the fix back to the mirror, so redo it if that happens. Verify with
tests/build, not `uv lock --locked` (which flags harmless mirror-vs-public
metadata diffs like missing `size`/`upload-time`).
