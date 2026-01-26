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

# Reports (group-by: status, priority, issuetype, assignee, labels, components, parent)
zaira report --board 123 --group-by status  # Generate report from board
zaira report my-tickets --full              # Named report + export tickets
zaira report --dashboard 123                # Report from Jira dashboard
zaira report --jql "project = FOO" --files  # Force file output
zaira report --jql "..." -g components      # Group by component
zaira refresh sprint-review.md              # Refresh existing report

# View tickets
zaira my                                    # Show my assigned tickets
zaira my -r                                 # Show tickets I reported (created)
zaira boards                                # List boards

# Create ticket from YAML front matter
zaira create ticket.md                      # Create from file
zaira create - --dry-run                    # Preview from stdin

# Edit ticket fields
zaira edit FOO-1234 --title "New title"
zaira edit FOO-1234 --description "New description"
zaira edit FOO-1234 --field "Priority=High" --field "Epic Link=FOO-100"
zaira edit FOO-1234 --field "assignee=me"   # Assign to yourself
zaira edit FOO-1234 --field "assignee=user@example.com"  # Assign by email
zaira edit FOO-1234 --from fields.yaml      # Update from YAML file
zaira edit FOO-1234 --from -                # Update from stdin YAML

# Other actions
zaira comment FOO-1234 "Comment text"       # Add comment to ticket
zaira link FOO-1234 FOO-5678 --type Blocks  # Link tickets
zaira transition FOO-1234 "In Progress"     # Change ticket status
zaira transition FOO-1234 --list            # List available transitions

# Instance metadata (cached locally)
zaira info statuses                         # List statuses
zaira info fields                           # List custom fields
zaira info fields --refresh                 # Refresh from Jira API
zaira info components FOO                   # List components for project
zaira info labels FOO                       # List labels for project
zaira info --save                           # Refresh all metadata
```

## Jira Formatting

When editing ticket descriptions or comments, use Jira wiki markup (not markdown):

```
h1. Heading 1
h2. Heading 2
h3. Heading 3

* Bullet item
* Another item

# Numbered item
# Another numbered item

*bold*  _italic_  -strikethrough-
[link text|https://example.com]
{code}code block{code}
```

## Confluence Wiki

Access Confluence pages using the same Jira credentials:

```bash
# Get page (outputs markdown with front matter)
zaira wiki get 123456                       # Get page by ID
zaira wiki get "https://acme.atlassian.net/wiki/spaces/DEV/pages/123456/Title"
zaira wiki get 123456 --format html         # Output raw HTML
zaira wiki get 123456 --format json         # Output full JSON response

# Bulk export pages
zaira wiki get 123 456 789 -o docs/         # Export multiple pages to directory
zaira wiki get 123 --children -o docs/      # Export page and all children
zaira wiki get 123 --list                   # List page tree without exporting

# Search pages
zaira wiki search "search terms"            # Search in title and body
zaira wiki search "API docs" --space TEAM   # Search in specific space
zaira wiki search --creator "John Doe"      # Find pages by creator
zaira wiki search "design" --format url     # Output just URLs

# Create page from markdown
zaira wiki create -s SPACE -t "Title" -m -b page.md
zaira wiki create -s SPACE -t "Title" -m -b -   # From stdin

# Sync markdown files to Confluence
zaira wiki put page.md                      # Push (page ID from front matter)
zaira wiki put docs/*.md                    # Push multiple files
zaira wiki put page.md --pull               # Pull remote changes to local
zaira wiki put page.md --status             # Check sync status
zaira wiki put page.md --diff               # Show local vs remote diff
zaira wiki put page.md --force              # Force push (overwrite conflicts)
zaira wiki put docs/*.md --create           # Create new pages for unlinked files

# Edit page properties
zaira wiki edit 123456 --title "New Title"
zaira wiki edit 123456 --parent 789         # Move under different parent
zaira wiki edit 123456 --labels "a,b,c"     # Set labels
zaira wiki edit 123456 --space NEWSPACE     # Move to different space

# Delete page
zaira wiki delete 123456                    # With confirmation prompt
zaira wiki delete 123456 --yes              # Skip confirmation

# Upload attachments
zaira wiki attach 123456 image.png          # Single file
zaira wiki attach 123456 *.png --replace    # Replace existing
```

### Wiki Front Matter

Files link to Confluence pages via YAML front matter. Title and labels sync automatically:

```yaml
---
confluence: 123456
title: My Page Title
labels: [docs, api, v2]
---

Page content here...
```

Images (`![alt](./images/foo.png)`) are uploaded as attachments on push and downloaded on pull.

## Programmatic Access

```python
import zaira

# Jira client
jira = zaira.client()
issue = jira.issue("FOO-123")

# Instance schema (fields, statuses, priorities, issue types, link types)
s = zaira.schema()
s["statuses"]    # {'Open': 'To Do', 'In Progress': 'In Progress', ...}
s["fields"]      # {'customfield_10001': 'Epic Link', ...}
s["priorities"]  # ['Blocker', 'Critical', 'Major', ...]

# Project schema (components, labels)
ps = zaira.project_schema("FOO")
ps["components"]  # ['Backend', 'Frontend', ...]
ps["labels"]      # ['bug', 'feature', ...]
```

## Output

- `tickets/` - Exported ticket markdown files
- `reports/` - Generated reports
- `~/.cache/zaira/` - Cached schema (fields, statuses, etc.)

## Project Setup

```bash
zaira init FOO                              # Generate zproject.toml for project
zaira init FOO BAR                          # Multiple projects
zaira init FOO --force                      # Overwrite existing config
```

In a directory with `zproject.toml`, you can use named queries, report aliases, and batch operations.
