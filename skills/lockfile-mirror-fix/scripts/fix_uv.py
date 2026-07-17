"""Rewrite uv.lock's registry/package URLs from an internal registry
mirror back to public PyPI. Run from the directory containing uv.lock.
Run this last — a later `uv sync`/`uv lock`/`uv add` will silently
re-resolve against the mirror and undo it."""

import pathlib
import re

p = pathlib.Path("uv.lock")
text = p.read_text()
m = re.search(r'registry = "https://([^/]+)/simple"', text)
host = m.group(1) if m else None
if host and host != "pypi.org":
    text = text.replace(f"https://{host}/simple", "https://pypi.org/simple")
    text = text.replace(f"https://{host}/packages/", "https://files.pythonhosted.org/packages/")
    p.write_text(text)
print(f"replaced host: {host or 'none found'}")
