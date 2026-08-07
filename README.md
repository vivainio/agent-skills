# agent-skills

A collection of shareable Claude Code skills.

## Installation

Via [skillset](https://github.com/vivainio/skillset):

```bash
uvx skillset add vivainio/agent-skills                    # all skills, prompts to select
uvx skillset add vivainio/agent-skills -p extra-skills     # extra skills only
```

## Available Skills

- **tasks-py** - Create and maintain zero-dependency Python task runner files
- **python-project** - Set up modern Python projects with uv and pyproject.toml
- **public-github** - Set up public GitHub repos with SSH authentication and PyPI publishing
- **chat-transcript** - Capture and save the current AI chat session as a markdown transcript file
- **lockfile-mirror-fix** - Fix `package-lock.json`/`uv.lock` entries that got resolved against an internal registry mirror instead of the public one, breaking CI that can't reach the mirror
- **kiss** - Keep It Simple, Stupid — terse-communication and minimal-everything mode
- **github-release** - Create GitHub releases with release notes using the `gh` CLI
- **worktree-done** - Wrap up a finished git worktree (manual-only, `/worktree-done`)

## Extra Skills

Extra skills (`extra-skills/`) are more opinionated than the core skills. They encode specific workflows and conventions that may conflict with habits or other skills you already have installed. Install them only if you want to adopt the workflow they prescribe.

- **zipget** - Download and install tools from GitHub releases, URLs, or S3 using [zipget-rs](https://github.com/vivainio/zipget-rs)
- **vp-code-review** - Review a pull request or branch diff
- **leo-editor** - Work on the leo-editor codebase: sync `.leo` outline files with edited source via leoBridge, run its test/lint/type-check suite

## Creating Skills

Each skill lives in its own directory under `skills/`:

```
skills/
└── your-skill-name/
    └── SKILL.md
```

## License

MIT
