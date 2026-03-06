# Spec Template

Use this minimal template when creating a new spec file in `specs/`.

```markdown
# <feature-name>

## What
One or two sentences describing the feature.

## Why
Motivation or context. What problem does this solve?

## Acceptance Criteria

### AC-1: <name>
- Concrete, verifiable behavior

### AC-2: <name>
- Concrete, verifiable behavior

## Decisions
Key design decisions made (e.g. approach chosen, alternatives rejected).

## Tickets
Relevant work tickets (e.g. PROJ-123). Remove section if not applicable.

## Open questions
Anything unresolved. Remove section if empty.

## Shipped
Commit or PR where this landed, and date. Remove section until shipped.
```

## Notes

- Keep it short. A spec that fits on one screen is better than one that doesn't.
- Acceptance criteria should be numbered (AC-1, AC-2, ...) for traceability to test-plan.md.
- Update the **Decisions** section as implementation progresses.
- It is fine to leave sections empty or remove them if not applicable.
