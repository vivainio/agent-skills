---
name: zoxide-find
description: Find a local directory or repo checkout by name using zoxide. Use when you need to locate a repo or project directory on this machine instead of guessing paths or re-cloning.
---

# zoxide-find

Use `zoxide query -l <keywords>` to find a repo, not `find` or guessed paths. Plain `query` returns only the top hit, which may be wrong. Matches are visited directories, not necessarily repos, and subdirectories can outrank the root. Confirm the `.git` root before using one. If nothing matches, ask or clone.
