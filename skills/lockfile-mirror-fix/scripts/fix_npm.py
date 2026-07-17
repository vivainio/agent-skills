"""Rewrite package-lock.json's resolved URLs from an internal registry
mirror back to the public npm registry. Run from the directory containing
package-lock.json."""

import pathlib
import re

p = pathlib.Path("package-lock.json")
text = p.read_text()
hosts = set(re.findall(r'"resolved": "https://([^/]+)/', text)) - {"registry.npmjs.org"}
for host in hosts:
    text = text.replace(f"https://{host}/", "https://registry.npmjs.org/")
p.write_text(text)
print(f"replaced hosts: {hosts or 'none found'}")
