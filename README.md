# agent-skills

A collection of shareable Claude Code skills.

## Installation

```bash
git clone git@github.com:vivainio/agent-skills.git
cd agent-skills
python install.py
```

This symlinks skills to `~/.claude/skills/`. Edits to the repo update immediately.

## Available Skills

- **tasks-py** - Create and maintain zero-dependency Python task runner files
- **python-project** - Set up modern Python projects with uv and pyproject.toml

## Creating Skills

Each skill lives in its own directory under `skills/`:

```
skills/
└── your-skill-name/
    └── SKILL.md
```

## License

MIT
