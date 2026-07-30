---
name: worktree-done
description: Wrap up a finished git worktree. Manual-only, invoked via `/worktree-done`.
disable-model-invocation: true
---

# Worktree done

Before deleting anything, verify the work actually landed where it belongs:
right base branch (don't assume `main` — check what it really branched
from), actually merged/cherry-picked/PR'd, nothing uncommitted left behind
in the worktree. Only then delete the branch.

Leave removing the worktree checkout directory itself to the user — don't
`git worktree remove` / `ExitWorktree` it.

Ask before force-deleting, or before pushing to a remote.
