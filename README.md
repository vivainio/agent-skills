# agent-skills

A collection of shareable Claude Code skills.

## Installation

```bash
git clone git@github.com:vivainio/agent-skills.git
cd agent-skills
python install.py
```

This symlinks skills to `~/.claude/skills/`. Edits to the repo update immediately.

To also install extra skills:

```bash
python install.py --extra
```

## Available Skills

- **tasks-py** - Create and maintain zero-dependency Python task runner files
- **python-project** - Set up modern Python projects with uv and pyproject.toml
- **public-github** - Set up public GitHub repos with SSH authentication and PyPI publishing
- **zaira** - Access Jira tickets offline using the [zaira](https://github.com/vivainio/zaira) CLI

## Extra Skills

Extra skills (`extra-skills/`) are more opinionated than the core skills. They encode specific workflows and conventions that may conflict with habits or other skills you already have installed. Install them only if you want to adopt the workflow they prescribe.

- **zipget** - Download and install tools from GitHub releases, URLs, or S3 using [zipget-rs](https://github.com/vivainio/zipget-rs)
- **mspec** - Spec-driven design workflow that writes plans and requirements to a `specs/` directory. Opinionated about file layout and when Claude should write specs vs. just code. The premise is that heavier SDD systems were designed for dumber AI models — this one tries to prove you don't need that much scaffolding anymore. Key conventions:
  - `specs/` is always a symlink into another repository (not the project repo)
  - Each feature gets a `spec.md` using a minimal template (What, Why, Decisions, Shipped)
  - `## Shipped` is added on completion with commit/PR reference and date
  - WIP features: `grep -rL "## Shipped" specs/ --include="spec.md"`
  - Optional companion files: `research.md`, `testing.md`, diagrams alongside `spec.md`

## Creating Skills

Each skill lives in its own directory under `skills/`:

```
skills/
└── your-skill-name/
    └── SKILL.md
```

## License

MIT
