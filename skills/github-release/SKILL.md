---
name: github-release
description: Create GitHub releases with release notes using gh CLI. Use when publishing a new release, generating changelogs, or creating release notes from commits.
---

# GitHub Release

Create GitHub releases with release notes using the `gh` CLI. Do NOT create or push git tags — the GitHub Action will patch in the correct version.

## Workflow

### 1. Ensure correct gh auth

Check the remote URL to determine whether this is a public or work repository, then switch `gh` to the matching account:

```bash
# If the GitHub username in the remote URL contains "_", it's a work repo; otherwise it's public
git remote -v | head -1 | grep -q '_/' && gh auth switch --user <work_user> || gh auth switch --user <public_user>
```

### 2. Verify local commits are pushed (CRITICAL)

`gh release create` cuts the tag from GitHub, not your local copy. Unpushed commits → release built from stale code. Push and confirm sync first:

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH" && git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/$BRANCH)" \
  && echo "in sync ✓" || echo "OUT OF SYNC — do not release"
```

Proceed only on `in sync ✓`. If push fails, stop and fix it — don't release against a stale remote.

### 3. Determine the release version

Fetch existing tags to understand the current versioning:

```bash
git fetch --tags
git tag --sort=-v:refname | head -5
```

Determine the next version by bumping the appropriate segment (major/minor/patch) based on the changes. Ask the user to confirm if ambiguous.

### 4. Generate release notes

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

### 5. Create the release

```bash
gh release create <version> \
  --title "<version>" \
  --notes "$(cat <<'EOF'
<release notes here>
EOF
)"
```

### Rules

- **Push and verify sync first (step 2).** Never release until local HEAD == remote target branch — the #1 cause of shipping wrong code.
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
