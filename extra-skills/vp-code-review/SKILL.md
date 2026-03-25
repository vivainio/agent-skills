---
name: vp-code-review
description: "Code review a pull request or branch diff. Use when user says /vp-code-review, asks to review a PR, review changes, or review code."
---

# vp-code-review

Wrapper around the `code-review` skill that ensures the correct `gh` auth account is active before reviewing.

## Usage

```
/vp-code-review [PR_NUMBER | BRANCH | URL]
```

- No argument: review current branch vs base branch
- PR number: `gh pr view <number>` to get context, then review the diff
- Branch name: diff against main/master
- GitHub PR URL: extract PR number and review

## Workflow

### 1. Ensure repo is cloned locally

If the current directory is not the target repository (e.g. user provided a PR URL or repo name for a different project), use `/ppm` to clone it first:

```bash
ppm clone <org/repo>
```

Then `cd` into the cloned repo before proceeding.

### 2. Check out the PR branch via worktree

The existing clone is likely on a different branch. Do not switch branches — create a temporary git worktree instead:

```bash
git fetch origin
git worktree add /tmp/review-<repo>-<pr> <pr-branch>
cd /tmp/review-<repo>-<pr>
```

This avoids disturbing any in-progress work in the main checkout. Clean up the worktree after the review is complete:

```bash
git worktree remove /tmp/review-<repo>-<pr>
```

### 3. Ensure correct gh auth

Check the remote URL to determine whether this is a public or work repository, then switch `gh` to the matching account:

```bash
# If the GitHub username in the remote URL contains "_", it's a work repo; otherwise it's public
git remote -v | head -1 | grep -q '_/' && gh auth switch --user <work_user> || gh auth switch --user <public_user>
```

### 4. Cross-check PR against Jira ticket

Extract the Jira ticket key from the PR title, branch name, or description (e.g. `FOO-123`). Then use `/zaira` to fetch the ticket:

```bash
zaira get FOO-123
```

Compare the PR changes against the ticket's description and acceptance criteria. Flag in the review if:
- The PR does work not described in the ticket
- The ticket has acceptance criteria the PR doesn't address
- The PR title/description doesn't match the ticket's intent

### 5. Present context to the reviewer

Before running the automated review, present a brief summary to the user:

- **Ticket**: key, summary, and acceptance criteria from Jira
- **PR scope**: files changed, type of change (feature/bugfix/refactor)
- **Mismatches**: any discrepancies found between the PR and ticket in step 3

Ask the user:
- Is there anything specific to focus on or watch out for?
- Any context the automated review wouldn't know (e.g. ongoing refactors, known tech debt)?

Wait for the user's input before proceeding.

### 6. Run code review

Invoke `/code-review:code-review` with the provided arguments. It runs a multi-agent review pipeline that handles gathering the diff, reviewing files, scoring issues, and commenting on the PR.

### 7. Review findings with the user

Present the automated review results to the user. For each finding, ask the user to confirm or dismiss. Especially surface:

- Findings where the severity is ambiguous
- Issues that might be intentional trade-offs
- Anything that contradicts the user's input from step 4

The user decides the final verdict (approve / request changes / comment). Do not post the review comment on the PR without the user's approval.

If the review revealed that the Jira ticket description or acceptance criteria are outdated, incomplete, or don't match what the PR actually does, suggest updating the ticket via `/zaira`.
