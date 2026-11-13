---
name: zensical-publishing
description: Set up and publish a Zensical documentation book (zensical.toml, GitHub Pages workflow, local preview, strict build) and add the bundled reading tools — click-to-zoom Mermaid diagrams, full-screen tables, Nav/TOC/Wide layout toggles. Use when creating a Zensical docs site, wiring up its publish workflow, or adding diagram zoom / a wider reading layout to an existing Zensical book.
---

# zensical-publishing

[Zensical](https://zensical.org) builds a static docs site from Markdown and a `zensical.toml`.
This skill covers getting a book built and published, and the reading tools it can bundle.

## 1. The book

Layout: a docs directory of Markdown plus `zensical.toml` at the repo root.

```toml
[project]
site_name = "My Book"
site_description = "One sentence."
site_url = "https://<owner>.github.io/<repo>/"   # must match where it is published
docs_dir = "docs"
nav = [{ "Home" = "index.md" }]
```

Look at an existing book in the same account for theme, palette and Markdown extensions and copy
those rather than inventing a style. Mermaid diagrams need the fence declared:

```toml
[project.markdown_extensions."pymdownx.superfences"]
custom_fences = [{ name = "mermaid", class = "mermaid" }]
```

Preview locally: `uvx zensical serve` (add `-f <config>` for a config not named `zensical.toml`).
Check before pushing: `uvx zensical@<version> build --strict`, using the version the workflow pins.
Output goes to `site/` (add it to `.gitignore`). `--strict` makes a broken link or anchor an error.

A repository can hold several books: one `zensical.<name>.toml` per book, each with its own
`docs_dir` and `site_dir`, built with `-f`.

## 2. Publish to GitHub Pages

Settings → Pages → Source: **GitHub Actions** (or `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`).
Then `.github/workflows/docs.yml`:

```yaml
name: Documentation
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "zensical.toml"
      - ".github/workflows/docs.yml"
concurrency:
  group: pages
  cancel-in-progress: true
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v6
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v5
      - run: uv tool run zensical@<version> build --clean --strict
      - uses: actions/upload-pages-artifact@v5
        with:
          path: site
      - uses: actions/deploy-pages@v5
        id: deployment
```

Pin the Zensical version (`zensical@<version>`) so a release cannot break the publish. Take the action
versions from a workflow in the user's other books if they have one: they are the ones known to work.
Include in `paths:` every directory that feeds the build (docs, shared asset folders, the config).
A push republishes the site, so build locally first.

## 3. Reading tools

`assets/reading-tools.css` and `assets/reading-tools.js` (next to this `SKILL.md`) add to any
Zensical site:

- **Mermaid zoom:** click a diagram to open it full screen, scaled to fit. Zoom with the buttons,
  `+` / `-` / `0`, or Ctrl + wheel / trackpad pinch; drag to pan; `Esc` closes.
- **Tables:** a "Full screen" button above every plain table.
- **Layout toggles** (wide screens): hide the navigation, hide the table of contents, use the full
  window width. Remembered across pages (localStorage, so per origin).

Self-contained: no dependencies, no configuration. Do not edit a book's copy; a change belongs in
this skill so every book can take it.

### Add to or update a book

1. Check the book uses Zensical's theme (the script relies on `.md-typeset` and `div.mermaid`). If
   not, stop and say so. The installer cannot check this.
2. Run the installer from the book's repository (`<skill dir>` is the folder holding this file):

   ```bash
   python3 <skill dir>/scripts/install.py              # all zensical*.toml in the repo
   python3 <skill dir>/scripts/install.py --shared docs-shared   # several books: one shared copy, per-file symlinks
   python3 <skill dir>/scripts/install.py --check      # change nothing; exit 1 if stale
   ```

   It copies (or symlinks, with `--shared`; Zensical follows file symlinks, not directory ones, so
   copy instead where contributors lack symlinks) the files into `<docs_dir>/assets/reading-tools/`,
   appends them to `extra_css` / `extra_javascript` (in `[project]` when the config has that table,
   else top level) without touching other entries, and warns if the workflow's `paths:` filter does
   not cover them. It is idempotent, so the same command updates a book whose copy is out of date.
   `--dry-run` previews. Fix any `WARN` by adding the path to the workflow's `paths:`.3. Build `--strict`, serve, and check in a browser that clicking a diagram opens the zoom view and
   the toolbar appears. `zensical serve` does not see edits to symlink targets: restart it.
4. Mention the tools in the book's README in a line or two. When updating, say what changed.

### How it works (for changing the tools)

Zensical renders each Mermaid diagram into a **closed shadow root**, so the page cannot read the SVG
back. The script patches `Element.prototype.attachShadow` to open it for `.mermaid` hosts, then
copies the rendered SVG into the zoom view. That is why it must load before the diagrams render.
CSS classes use the `od-` prefix and the storage key is `onp-docs-layout`; they are internal, and
renaming them resets readers' saved layout.
