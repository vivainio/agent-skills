"""Rewrite uv.lock's registry/package URLs from an internal registry
mirror back to public PyPI. Run from the directory containing uv.lock.
Run this last — a later `uv sync`/`uv lock`/`uv add` will silently
re-resolve against the mirror and undo it."""

import pathlib
import re

p = pathlib.Path("uv.lock")
text = p.read_text()
m = re.search(r'registry = "(https://[^"]+)/simple"', text)
prefix = m.group(1) if m else None
if prefix and prefix != "https://pypi.org":
    text = text.replace(f"{prefix}/simple", "https://pypi.org/simple")
    text = text.replace(f"{prefix}/packages/", "https://files.pythonhosted.org/packages/")
    # some mirrors (e.g. Artifactory) double the packages/ segment in package URLs
    text = text.replace("files.pythonhosted.org/packages/packages/", "files.pythonhosted.org/packages/")
    p.write_text(text)
print(f"replaced prefix: {prefix or 'none found'}")
