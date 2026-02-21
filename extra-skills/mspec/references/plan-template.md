# Plan Template

Use this template when writing `plan.md` during plan mode.

```markdown
# Plan: <feature-name>

## Approach
Brief summary of the implementation strategy.

## Steps
1. ...
2. ...
3. ...

## Files affected
- `path/to/file.py` — what changes and why
- ...

## Risks / tradeoffs
Anything that could go wrong or was a close call.

## Out of scope
What is explicitly not being done here.
```

## Notes

- `plan.md` is temporary — it exists to communicate intent, not to persist
- After shipping, fold **Risks / tradeoffs** and key decisions into `spec.md` Decisions section, then delete `plan.md`
- Keep it short enough to read in one sitting
