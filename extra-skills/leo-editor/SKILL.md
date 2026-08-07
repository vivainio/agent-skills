---
name: leo-editor
description: "Work on the leo-editor codebase (leo-editor/leo-editor). Use when editing leo-editor's own source, since its .py/.toml/.txt files are round-tripped from .leo outline files (like leo/core/LeoPyRef.leo) that go stale after a plain-text edit unless synced back via leoBridge. Also covers running its test/lint/type-check suite and known test quirks."
---

# leo-editor development

Leo (leo-editor) is a self-hosting outline editor: much of its own source is
tracked *both* as plain files (`.py`, `.toml`, `.txt`) *and* as nodes inside
`.leo` outline files (XML). Editing the plain file with a normal text editor
is exactly what you'll do — but it leaves the mirrored `.leo` outline stale,
which matters if the maintainer works in the Leo GUI. This skill covers how
to detect that, and re-sync it headlessly without needing the GUI.

## Is a file mirrored in an outline?

Check its first line:

```bash
head -1 path/to/file.py
```

- Starts with `# @+leo-ver=5-thin` (or `#@+leo-ver=...`, `# @+leo-ver=...`)
  → it's an `@file` node. The sentinel comments in the file *are* the source
  of truth for outline structure; Leo reconstructs the tree by reading them.
- No sentinel line → either not tracked in an outline at all, or it's an
  `@clean` node, where the *outline* holds the full body and the external
  file is derived from it with no sentinels. `setup.cfg` is a real example
  of this in leo-editor.

Either way, don't try to figure out which case you're in before fixing it —
`refresh-from-disk` (below) handles both identically.

Find which `.leo` file mirrors a given source file with a quick grep for its
relative path inside candidate outlines (leo-editor's own source tree is
mirrored in `leo/core/LeoPyRef.leo`):

```bash
grep -n "@file ../commands/checkerCommands.py" leo/core/LeoPyRef.leo
```

## Re-syncing an outline from edited files (leoBridge)

Leo ships a headless scripting API, `leo.core.leoBridge`, built for exactly
this. Don't hand-edit the outline's XML to mirror a content change (risky,
tedious, and pointless busywork) — open the outline, call
`c.refreshFromDisk(p)` for each `@<file>` node whose backing file you
touched, then save.

```python
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')  # no GUI/display needed
from leo.core import leoBridge

repo = os.path.abspath('.')
bridge = leoBridge.controller(
    gui='nullGui', loadPlugins=False, readSettings=False, silent=True, verbose=False,
)
c = bridge.openLeoFile(os.path.join(repo, 'leo/core/LeoPyRef.leo'))

changed_files = [
    'leo/commands/checkerCommands.py',
    'setup.cfg',   # @clean node — refreshFromDisk handles this the same way.
]
changed_full = {os.path.normpath(os.path.join(repo, f)) for f in changed_files}

refreshed = []
for full in changed_full:
    for p in c.all_positions():
        if p.isAnyAtFileNode() and os.path.normpath(c.fullPath(p)) == full:
            c.refreshFromDisk(p=p)
            refreshed.append(full)
            break
print("refreshed:", refreshed)
print("missing:", changed_full - set(refreshed))  # should be empty

ok = c.fileCommands.save(os.path.join(repo, 'leo/core/LeoPyRef.leo'))
print("save ok:", ok)
```

Notes:
- `openLeoFile` prints `can not open <path>` for every `@<file>` node whose
  external file is currently missing. This is normal noise for files that
  are *already* gone (including ones you're about to delete in the next
  step) or for pre-existing stale references unrelated to your change —
  don't treat it as a failure by itself.
- Do all your plain-file edits first, run tests/lint against them, *then*
  do one refresh pass covering everything you touched. If you make a
  follow-up edit to an already-refreshed file, refresh it again — the sync
  isn't automatic or continuous.
- `refreshFromDisk` is explicitly documented as not undoable. That's fine
  headlessly since the repo (git) is your undo; just don't run this against
  uncommitted outline changes you care about without a backup.

## Deleting nodes structurally

`refreshFromDisk` re-syncs a node's *content*; it won't remove a node whose
backing file you deleted, or a settings node you want gone entirely. Delete
those explicitly:

```python
def delete_by_path_suffix(suffix):
    for p in c.all_positions():
        if p.isAnyAtFileNode() and os.path.normpath(c.fullPath(p)).endswith(suffix):
            p.doDelete()
            return True
    return False

delete_by_path_suffix('scripts/dead_script.py')

def delete_by_headline(h):
    for p in c.all_positions():
        if p.h.strip() == h:
            p.doDelete()
            return True
    return False

delete_by_headline('@bool some-removed-setting = False')
```

Re-scan and delete one at a time (don't collect a batch of `Position`
objects up front and delete them in a loop) — `doDelete()` shifts sibling
child indices, invalidating any other `Position` you captured earlier for a
node under the same parent.

## Verifying the outline afterward

Always check these three things after a sync/delete pass, before trusting
the result:

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('leo/core/LeoPyRef.leo'); print('XML OK')"
```

```python
# Re-open with leoBridge — confirms no structural corruption, and lets you
# assert specific nodes are gone/present.
c = bridge.openLeoFile(os.path.join(repo, 'leo/core/LeoPyRef.leo'))
print(len(list(c.all_positions())))
```

```bash
git diff --stat leo/core/LeoPyRef.leo   # sanity-check the size of the change
```

Take a backup copy of the outline file before a bulk automated pass if
you're not confident (`cp file.leo /tmp/file.leo.bak`) — cheap insurance
against a scripting mistake on a file that's otherwise tedious to
reconstruct by hand.

## Testing a new Leo command headlessly

You can exercise Leo commands and their classes directly through the bridge
without a GUI — useful for verifying a new `@g.command(...)` actually
registers and behaves correctly before you trust it:

```python
c = bridge.openLeoFile(os.path.join(repo, 'leo/core/LeoPyRef.leo'))
print('my-command' in c.commandsDict)          # registration check

from leo.commands.checkerCommands import RuffCommand
p = c.rootPosition().insertAfter()
p.h = '@file /tmp/scratch_test.py'             # point at a real scratch file
ok = RuffCommand(c).check_on_write(p)          # call the class method directly
```

## Running the test/lint/type-check suite

```bash
QT_QPA_PLATFORM=offscreen python -m pytest leo/unittests   # no real display needed
ruff check leo                                              # config: ruff.toml (NOT pyproject.toml — its presence overrides [tool.ruff] there)
python -m mypy leo
```

CI itself (`.github/workflows/ci.yml`) is the authoritative source for exact
invocations and matrix versions.

### Known quirks, not regressions

- **`mypy leo` is occasionally flaky**: a spurious `Cannot determine type of
  "x" [has-type]` error can appear on a class you never touched (seen on
  `leoShadow.py` after an unrelated edit elsewhere). Clear `.mypy_cache` and
  re-run 2-3 times before concluding you broke something — if it's real,
  it reproduces every time; if it clears up, it was a one-off inference
  race.
- **Don't pass extra flags to `pytest` blindly**: `test_g_OptionsUtils` (in
  `test_leoGlobals.py`) exercises Leo's own CLI-option parser using the
  *actual* `sys.argv` of the pytest process, so flags like `-x` or `-q` can
  make that one test fail with `SystemExit: 1` / "Unknown option" — it's
  not related to whatever you're testing. Re-run without extra flags (or
  scope with `-k`, which doesn't add a positional/short flag) to confirm.
- **`# pylint: disable=...` / `# for pyflakes` comments are everywhere** in
  the codebase, left over from when those tools were used ad hoc (mostly
  removed as of #4855, ruff is now the single linter). They're inert dead
  comments now. Don't mass-delete them as drive-by cleanup — massive diff,
  zero functional value, not what anyone asked for.
- **`@nopylint`/`@nopyflakes` are outline *directives*, not the tools**:
  headline/body markers like `@nopylint` are still read by some commands
  (`find-long-lines`, `find-missing-docstrings`) to exclude a subtree, even
  though the pylint tool itself is gone. Don't confuse "the directive still
  works" with "the tool still runs".
