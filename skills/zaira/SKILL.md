---
name: zaira
description: Access Jira tickets offline using zaira CLI. Use when user needs to export, report, or refresh Jira tickets, or mentions "jira", "zaira", or ticket keys like "FOO-123".
---

# Zaira - Jira CLI

Exports Jira tickets to local markdown for offline access. See https://github.com/vivainio/zaira for setup.

## Commands

```bash
# Export tickets
zaira export FOO-1234 FOO-5678              # Export specific tickets
zaira export --jql "project = FOO"          # Export by JQL query
zaira export FOO-1234 --all-fields          # Include custom fields
zaira export FOO-1234 --files               # Force file output without zproject.toml

# Reports
zaira report --board 123 --group-by status  # Generate report from board
zaira report my-tickets --full              # Named report + export tickets
zaira report --dashboard 123                # Report from Jira dashboard
zaira report --jql "project = FOO" --files  # Force file output
zaira refresh sprint-review.md              # Refresh existing report

# View tickets
zaira my                                    # Show my open tickets
zaira boards                                # List boards

# Create ticket from YAML front matter
zaira create ticket.md                      # Create from file
zaira create - --dry-run                    # Preview from stdin

# Edit ticket fields
zaira edit FOO-1234 --title "New title"
zaira edit FOO-1234 --description "New description"
zaira edit FOO-1234 --field "Priority=High" --field "Epic Link=FOO-100"
zaira edit FOO-1234 --from fields.yaml      # Update from YAML file
zaira edit FOO-1234 --from -                # Update from stdin YAML

# Other actions
zaira comment FOO-1234 "Comment text"       # Add comment to ticket
zaira link FOO-1234 FOO-5678 --type Blocks  # Link tickets
zaira transition FOO-1234 "In Progress"     # Change ticket status

# Instance metadata (cached locally)
zaira info statuses                         # List statuses
zaira info fields                           # List custom fields
zaira info fields --refresh                 # Refresh from Jira API
zaira info --save                           # Refresh all metadata
```

## Confluence Wiki

Access Confluence pages using the same Jira credentials:

```bash
zaira wiki get 123456                       # Get page by ID
zaira wiki get "https://acme.atlassian.net/wiki/spaces/DEV/pages/123456/Title"
zaira wiki get 123456 --format md           # Output as markdown (default)
zaira wiki get 123456 --format html         # Output raw HTML
zaira wiki get 123456 --format json         # Output full JSON response
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
- `~/.cache/zaira/` - Cached schema (fields, statuses, etc.)

## Advanced Usage

In a directory with `zproject.toml`, you can use named queries, report aliases, and batch operations. See `zaira init --project FOO` to generate one.
