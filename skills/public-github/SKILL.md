---
name: public-github
description: Set up public GitHub repos with SSH authentication and PyPI publishing. Use when creating open source projects or configuring github-public host alias.
---

# Public GitHub Setup

Configure public GitHub repositories with SSH authentication and PyPI trusted publisher.

## SSH Config for Multiple Accounts

Use SSH host aliases to distinguish between public (personal) and private (work) GitHub accounts.

### ~/.ssh/config

```
# Private/work GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work

# Public GitHub
Host github-public
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_public
```

### Usage

For **public** repositories, use `github-public` host alias:

```bash
git remote add origin git@github-public:someuser/myproject.git
```

For **private/work** repositories, use standard `github.com`:

```bash
git remote add origin git@github.com:company/repo.git
```

### Verify

```bash
git remote -v
# origin  git@github-public:someuser/myproject.git (fetch)
# origin  git@github-public:someuser/myproject.git (push)
```

## PyPI Publishing with Trusted Publishers

Use GitHub Actions with OIDC authentication (no API tokens needed).

### 1. Configure PyPI Trusted Publisher

Go to https://pypi.org/manage/account/publishing/ and add:

| Field | Value |
|-------|-------|
| PyPI project name | `your-package-name` |
| Owner | Your GitHub username |
| Repository | Your repo name |
| Workflow name | `publish.yml` |
| Environment | `pypi` |

### 2. Create GitHub Environment

Go to repo Settings → Environments → New environment → name it `pypi`.

### 3. Add Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - name: Set version from release tag
        run: |
          VERSION="${{ github.ref_name }}"
          VERSION="${VERSION#v}"
          sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
          echo "Set version to $VERSION"

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### 4. Create Release

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --generate-notes
```

The workflow automatically extracts version from tag (strips `v` prefix) and publishes.

## gh CLI with Multiple Accounts

If `gh` commands fail with permission errors (e.g., "workflow scope may be required"), you may have the wrong account active.

### Check Active Account

```bash
gh auth status
```

Look for `Active account: true` to see which account is currently active.

### Switch Account

```bash
gh auth switch --user vivainio   # Switch to public account
gh auth switch --user work_user  # Switch to work account
```

### Verify and Retry

```bash
gh auth status                    # Confirm correct account is active
gh release create v0.1.0 ...     # Retry the command
```
