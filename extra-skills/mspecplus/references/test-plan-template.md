# Test Plan Template

Use this template when deriving a test plan from a spec. Create as `specs/<area>/<feature>/test-plan.md`.

```markdown
# <feature-name> — Test Plan

Spec: [spec.md](./spec.md)
Tests: [test_<feature>.py](../../tests/e2e/test_<feature>.py)

## Coverage Matrix

| Spec Item | Test Case | Level | Status |
|---|---|---|---|
| AC-1: <name> | test_<description> | E2E | Pending |
| AC-2: <name> | test_<description> | E2E | Pending |

## Test Data Requirements

- Describe what data each test needs
- Include preconditions and environment setup

## Deliberate Exclusions

- <What is not tested> — <why>

## Regression Notes

- <date>: Initial test plan derived from spec
```

## Notes

- One row per test case, not per spec item. A single AC may have multiple test cases.
- **Level** is typically `E2E` but can be `Unit`, `Integration`, or `Manual` when E2E is not appropriate.
- **Status** is `Pending` (no test yet), `Covered` (test exists and passes), or `Excluded` (deliberately not tested — must appear in Deliberate Exclusions).
- Update the coverage matrix as tests are written, not after the fact.
- Add to Regression Notes whenever the spec changes after initial creation.
- The Tests path is relative and may need adjusting per project structure.
