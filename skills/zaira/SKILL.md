---
name: zaira
description: Access Jira tickets offline using zaira CLI. Use when user needs to export, report, or refresh Jira tickets, or mentions "jira", "zaira", or ticket keys like "FOO-123".
---

# Zaira - Jira CLI

Exports Jira tickets to local markdown for offline access. See https://github.com/vivainio/zaira for setup.

## Commands

```bash
zaira export FOO-1234 FOO-5678         # Export specific tickets
zaira export --jql "project = FOO"     # Export by JQL query
zaira report --board 123 --group-by status  # Generate report
zaira report my-tickets --full         # Named report + export tickets
zaira refresh sprint-review.md         # Refresh existing report
zaira boards                           # List boards
zaira my                               # Show my open tickets
zaira comment FOO-1234 "Comment text"  # Add comment to ticket
zaira edit FOO-1234 -t "New title"    # Edit ticket title
zaira edit FOO-1234 -d "Description"  # Edit description (supports Jira wiki syntax)
zaira link FOO-1234 FOO-5678 -t Blocks # Link tickets
zaira transition FOO-1234 "In Progress" # Change ticket status
```

## Confluence Wiki

Access Confluence pages using the same Jira credentials:

```bash
zaira wiki get 123456                  # Get page by ID
zaira wiki get "https://acme.atlassian.net/wiki/spaces/DEV/pages/123456/Title"  # Get by URL
zaira wiki get 123456 --format md      # Output as markdown (default)
zaira wiki get 123456 --format html    # Output raw HTML
zaira wiki get 123456 --format json    # Output full JSON response
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
