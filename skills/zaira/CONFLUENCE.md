# Confluence Wiki

Access Confluence pages using the same Jira credentials (`zaira init`).

## Commands

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

## Front Matter

Files link to Confluence pages via YAML front matter. Title and labels sync automatically:

```yaml
---
confluence: 123456
title: My Page Title
labels: [docs, api, v2]
---

Page content here...
```

## Image Handling

Local images (`![alt](./images/foo.png)`) are automatically:
- Uploaded as Confluence attachments on push
- Downloaded to `images/` directory on pull
- Only re-uploaded when changed (hash-based tracking)
