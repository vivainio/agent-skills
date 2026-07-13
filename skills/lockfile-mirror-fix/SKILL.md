---
name: lockfile-mirror-fix
description: Replace internal registry mirror URLs in package-lock.json/uv.lock with public npm/pypi URLs. Never activates automatically — only engages after explicit `/lockfile-mirror-fix` invocation.
---

# lockfile-mirror-fix

Detect the mirror host from the lockfile itself (don't ask the user for
it) and replace it with the public registry, via plain string replace
after extraction — not a blind regex substitution:

**package-lock.json**:
```python
import pathlib, re
p = pathlib.Path("package-lock.json")
text = p.read_text()
hosts = set(re.findall(r'"resolved": "https://([^/]+)/', text)) - {"registry.npmjs.org"}
for host in hosts:
    text = text.replace(f"https://{host}/", "https://registry.npmjs.org/")
p.write_text(text)
```

**uv.lock**:
```python
import pathlib, re
p = pathlib.Path("uv.lock")
text = p.read_text()
m = re.search(r'registry = "https://([^/]+)/simple"', text)
host = m.group(1) if m else None
if host and host != "pypi.org":
    text = text.replace(f"https://{host}/simple", "https://pypi.org/simple")
    text = text.replace(f"https://{host}/packages/", "https://files.pythonhosted.org/packages/")
p.write_text(text)
```

Do this last — a later `uv sync`/`uv lock`/`uv add` will re-clobber it back
to the mirror, so redo it if that happens. Verify with tests/build, not
`uv lock --locked` (which flags harmless mirror-vs-public metadata diffs
like missing `size`/`upload-time`).
