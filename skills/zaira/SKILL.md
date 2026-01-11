---
name: zaira
description: Access Jira tickets offline using zaira CLI. Use when user needs to export, report, or sync Jira tickets, or mentions "jira", "zaira", or ticket keys like "FOO-123".
---

# Zaira - Jira CLI

Exports Jira tickets to local markdown for offline access. See https://github.com/vivainio/zaira for setup.

## Commands

```bash
zaira export FOO-1234 FOO-5678         # Export specific tickets
zaira export --jql "project = FOO"     # Export by JQL query
zaira report --board 123 --group-by status  # Generate report
zaira report my-tickets --full         # Named report + export tickets
zaira sync sprint-review.md            # Re-sync existing report
zaira boards                           # List boards
zaira my                               # Show my open tickets
```

## Programmatic Access

```python
import zaira
jira = zaira.client()
issue = jira.issue("FOO-123")
```

## Output

- `tickets/` - Exported ticket markdown files
- `reports/` - Generated reports

## Advanced Usage

In a directory with `zproject.toml`, you can use named queries, report aliases, and batch operations. See `zaira init --project FOO` to generate one.
