---
name: github-release
description: Create GitHub releases with release notes using gh CLI. Use when publishing a new release, generating changelogs, or creating release notes from commits.
---

# GitHub Release

Create GitHub releases with release notes using the `gh` CLI. Do NOT create or push git tags — the GitHub Action will patch in the correct version.

## Workflow

### 1-3. Preflight: gh auth, push/sync, CI green (CRITICAL)

Run the bundled script — it switches `gh` auth to the account matching this repo (public vs. work, detected from `gh auth status`'s logged-in accounts), pushes the current branch and verifies local HEAD matches `origin`, then polls CI for the exact pushed commit and requires `success`:

```bash
python3 scripts/preflight.py
```

`gh release create` cuts the tag from GitHub, not your local copy — unpushed commits mean a release built from stale code. The release tag is cut from the target branch's current HEAD, so if that commit's CI is failing, the release builds (and may publish) broken code.

Proceed only on `PREFLIGHT PASS`. On failure the script prints which check failed and exits non-zero — fix that (push, wait for CI, etc.) and re-run before releasing. (If no CI run exists for the repo at all, the script notes that and lets you proceed with judgement.)

### 4. Determine the release version

Fetch existing tags to understand the current versioning:

```bash
git fetch --tags
git tag --sort=-v:refname | head -5
```

Determine the next version by bumping the appropriate segment (major/minor/patch) based on the changes. Ask the user to confirm if ambiguous.

### 5. Generate release notes

Build release notes from the commit history since the last release:

```bash
# Find the latest release tag
gh release list --limit 1

# Show commits since that release
git log <previous-tag>..HEAD --oneline --no-decorate
```

Structure the notes into sections as appropriate:

- **New features** — new capabilities
- **Improvements** — enhancements to existing functionality
- **Bug fixes** — resolved issues
- **Breaking changes** — if any

Omit empty sections. Keep entries concise — one line per change.

### 6. Create the release

```bash
gh release create <version> \
  --title "<version>" \
  --notes "$(cat <<'EOF'
<release notes here>
EOF
)"
```

### Rules

- **Run preflight first (step 1-3).** Never release until `PREFLIGHT PASS` — local HEAD must match remote target branch (#1 cause of shipping wrong code) and CI must be green on that exact commit (the tag builds it as-is; a red `fmt`/`clippy`/`test` gate means a failed or broken-published release).
- **A release that fires a publish workflow is irreversible.** Once the publish-to-PyPI/npm run succeeds, that version is consumed — deleting/recreating the release or moving the tag won't help (the registry rejects re-uploads). If the code was wrong, **bump to the next patch and cut fresh.**
- **Do NOT create or push git tags.** The `gh release create` command creates the tag on GitHub automatically. Do not run `git tag` beforehand.
- **Do NOT edit project files** (e.g. version numbers in `pyproject.toml`, `package.json`, `Cargo.toml`). The GitHub Action handles version patching.
- **Do NOT use `--generate-notes`** as the sole source — always write curated notes from the commit log.
- **Target the current branch** unless the user specifies otherwise. Use `--target <branch>` if needed.
- **Draft releases** — use `--draft` if the user wants to review before publishing.
- **Pre-releases** — use `--prerelease` for alpha/beta/rc versions.

### Examples

Create a release:
```bash
gh release create v1.3.0 --title "v1.3.0" --notes "$(cat <<'EOF'
## New features
- Add offline export support
- Add CSV output format

## Bug fixes
- Fix crash when config file is missing
EOF
)"
```

Create a draft pre-release:
```bash
gh release create v2.0.0-rc1 --title "v2.0.0-rc1" --draft --prerelease --notes "$(cat <<'EOF'
## Breaking changes
- Removed deprecated `--legacy` flag

## New features
- New plugin system
EOF
)"
```
