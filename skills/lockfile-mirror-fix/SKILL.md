---
name: lockfile-mirror-fix
description: Replace internal registry mirror URLs in package-lock.json/uv.lock with public npm/pypi URLs. Never activates automatically — only engages after explicit `/lockfile-mirror-fix` invocation.
---

# lockfile-mirror-fix

Replace the mirror host with the public registry in the lockfile, via
plain string replace (not sed/regex):

**package-lock.json** — `resolved` URLs → `https://registry.npmjs.org/...`

**uv.lock**:
```python
text = text.replace('registry = "https://<mirror-host>/simple"', 'registry = "https://pypi.org/simple"')
text = text.replace("https://<mirror-host>/packages/", "https://files.pythonhosted.org/packages/")
```

Do this last — a later `uv sync`/`uv lock`/`uv add` will re-clobber it back
to the mirror, so redo it if that happens. Verify with tests/build, not
`uv lock --locked` (which flags harmless mirror-vs-public metadata diffs
like missing `size`/`upload-time`).
