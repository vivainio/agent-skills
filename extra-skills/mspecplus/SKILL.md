---
name: mspecplus
description: "Spec-driven design workflow with integrated test planning. Keeps specs and test plans in a `specs/` directory. Never activates automatically — only engages after explicit `/mspecplus` invocation. Also handles handovers: when the user requests one, update `plan.md` with current status and commit it."
---

# mspecplus

Everything from mspec, plus test-plan management for regression risk and E2E coverage.

## Workflow

### Starting a feature

1. Check if a spec already exists: `ls specs/` and scan for relevant area/feature directories
2. If no spec exists, identify the area and create `specs/<area>/<feature>/spec.md` using the template in `references/spec-template.md`
3. If no clear area exists yet, use `main` as the area (see Spec File Conventions)
4. Fill in **What** and **Why** at minimum — keep it to one screen
5. Show the spec to the user and get a nod before writing code

### Deriving the test plan

After the spec is reviewed and before (or alongside) implementation:

1. Create `specs/<area>/<feature>/test-plan.md` using the template in `references/test-plan-template.md`
2. Map each acceptance criterion from `spec.md` to one or more test cases in the coverage matrix
3. Document test data requirements and preconditions
4. Note deliberate exclusions with rationale — what is NOT tested at E2E level and why
5. Set initial coverage status to `Pending` for all entries
6. Show the test plan to the user before writing tests

The test plan references the spec but does not duplicate it. It references test code but does not contain it.

### During implementation

- Add to **Decisions** in `spec.md` as choices are made
- Move unresolved items to **Open questions**
- Update `test-plan.md` coverage status as tests are written (`Pending` → `Covered`)
- When a spec ambiguity is found during implementation, update both `spec.md` (add the clarification) and `test-plan.md` (add the test case)

### When the spec changes

This is where SDD earns its keep. The spec diff is the regression risk assessment.

**Step 1: Categorize every change in the spec diff**

Read the diff and classify each acceptance criterion into one of:

| Category | What happened | Example |
|---|---|---|
| **Added** | New AC that didn't exist before | `+ ### AC-6: Related document link` |
| **Modified** | Existing AC got new bullets or changed wording | `+ - Original invoice is linked as a related document` added under AC-1 |
| **Removed** | AC deleted or struck through | `- ### AC-3: Invoice type validation` |
| **Unchanged** | AC appears in both old and new spec, identical | AC-2 through AC-5 untouched |

**Step 2: Assess regression risk per category**

- **Added** — zero risk to existing behavior, but needs new test coverage
- **Modified** — low-to-medium risk; existing tests for that AC must still pass, new tests may be needed for the new bullets
- **Removed** — existing tests for that AC are now orphans; remove or reassign them
- **Unchanged** — must remain stable; existing tests are the regression safety net

**Worked example**

A team has a "Copy Invoice" spec with AC-1 through AC-5 and a test plan with 7 E2E tests, all `Covered`. A new requirement comes in. The spec diff:

```diff
  ### AC-1: Basic copy
  - Copied invoice appears in Draft status
  - User is taken to the new invoice details page
+ - Original invoice is linked as a related document on the copy

  ### AC-2: History
  - Invoice history shows "Invoice copied from <original_number>"

- ### AC-3: Invoice type validation
- - If the original invoice type is inactive or restricted, show error:
-   "Unable to copy invoice because invoice type is not valid"

  ### AC-4: Confidential invoices
- - Confidential invoices can only be copied by users with confidential rights
+ - Confidential invoices can only be copied by users with confidential rights
+   or by system administrators
  - Users without rights see: "Unable to copy a confidential invoice"

  ### AC-5: Copy as credit memo
  - For invoice documents, "Copy as credit memo" is available
  - Positive sums become negative on the copy

+ ### AC-6: Related document link
+ - The copy's related documents list contains the original invoice
+ - Clicking the link navigates to the original invoice
+ - If the original invoice is deleted, the link shows "Document no longer available"
```

Categorization:

| AC | Category | What happened |
|---|---|---|
| AC-1 | **Modified** | New bullet: related document link |
| AC-2 | Unchanged | — |
| AC-3 | **Removed** | Invoice type validation dropped from feature |
| AC-4 | **Modified** | System administrators added as allowed role |
| AC-5 | Unchanged | — |
| AC-6 | **Added** | Entirely new criterion |

Test plan update:

| Spec Item | Test Case | Status | Action |
|---|---|---|---|
| AC-1 | test_copied_invoice_is_draft | Covered | Keep as-is |
| AC-1 | test_copy_navigates_to_new_invoice | Covered | Keep as-is |
| AC-1 | test_copy_links_original_as_related_document | **Pending** | **New — added bullet** |
| AC-2 | test_copy_creates_history_entry | Covered | Keep as-is |
| ~~AC-3~~ | ~~test_copy_inactive_type_shows_error~~ | **Removed** | **Delete test** |
| AC-4 | test_copy_confidential_with_rights | Covered | Keep — still valid |
| AC-4 | test_copy_confidential_without_rights | Covered | Keep — still valid |
| AC-4 | test_copy_confidential_sysadmin_allowed | **Pending** | **New — added role** |
| AC-5 | test_copy_as_credit_memo_negates_sums | Covered | Keep as-is |
| AC-6 | test_related_document_link_navigates | **Pending** | **New AC** |
| AC-6 | test_related_document_deleted_unavailable | **Pending** | **New AC** |

Regression note:

```markdown
- 2026-03-03: AC-1 modified (added related doc link), AC-3 removed (type validation),
  AC-4 modified (sysadmin role), AC-6 added (related document link).
  Impact: AC-3 test to be deleted. AC-2, AC-5 unchanged — run as regression.
  New test cases: 4 (Pending). Removed: 1. Existing unchanged: 4.
```

Targeted regression run:

```
Changed: AC-1, AC-4, AC-6 → run 6 tests (3 existing + 3 new)
Unchanged: AC-2, AC-5      → run 2 tests (regression safety net)
Removed: AC-3               → delete test_copy_inactive_type_shows_error
Skip: unrelated features    → test_forward_invoice.py, test_image_viewer.py
```

**Step 3: Update test-plan.md**

For each category:

- **Added AC**: add new rows to the coverage matrix with status `Pending`. Identify test data requirements for the new cases.
- **Modified AC**: review existing rows for that AC. Keep rows that still apply. Add rows for new bullets with status `Pending`.
- **Removed AC**: mark rows as `Removed — AC deleted from spec`. Flag linked test code for deletion.
- **Unchanged AC**: no changes to the matrix. These tests will run as regression validation.

**Step 4: Add a regression note**

Add an entry to the Regression Notes section:

```markdown
- <date>: AC-1 modified (added related doc link), AC-6 added (related document link).
  Impact: additive change, no risk to AC-2 through AC-5.
  New test cases: 3 (Pending). Existing tests: 7 (unchanged, run as regression).
```

**Step 5: Plan the targeted regression run**

Based on the categorization, identify what to run:

- All tests for changed/added ACs (verifies new behavior)
- All tests for unchanged ACs in the same feature (verifies no regression within the feature)
- Tests for shared components touched by the change (verifies no cross-feature regression)
- Explicitly skip unrelated features

Document this in the regression note so the reasoning is preserved.

**Step 6: Fold the diff — return to clean state**

The spec diff, categorization table, and regression run plan are transient artifacts. They exist during the change to make regression risk visible. Once the work is done:

1. `spec.md` is updated to its new state — it shows only current truth, no diff markers, no history of what was removed or changed. AC-3 is simply gone. AC-6 is simply there. AC-4 reads as if it always included sysadmins.
2. `test-plan.md` coverage matrix is cleaned up — removed rows are deleted (not struck through), pending rows become `Covered`, the matrix reflects the current spec exactly.
3. The **Regression Notes** section in `test-plan.md` is the only place the change history survives. It's a log, not a diff — short entries recording what changed and when.

After folding, the three artifacts are again in sync and self-contained. Someone reading them for the first time sees the current feature, not its evolution. The git history preserves the actual diffs for anyone who needs the archeology.

```
Before change:     spec.md (v1) ↔ test-plan.md (v1) ↔ tests (v1)   ← clean state
During change:     spec diff → categorization → risk assessment      ← transient
After folding:     spec.md (v2) ↔ test-plan.md (v2) ↔ tests (v2)   ← clean state again
                                  └─ Regression Notes: log entry
```

This is per-feature. Each `specs/<area>/<feature>/` directory goes through this cycle independently. A change to Copy Invoice does not touch the Forward Invoice spec or test plan.

### Handover

When the user requests a handover, write `plan.md` capturing current status: what's done, where things stopped, any loose context or decisions not yet in `spec.md`, test coverage gaps from `test-plan.md`, and what to do next. Then commit it.

### After shipping

- Fold key decisions and outcomes from `plan.md` into the **Decisions** section of `spec.md`
- Fill in the **Shipped** section with the commit or PR reference and date
- Verify `test-plan.md` has no `Pending` entries — all criteria should be `Covered` or explicitly excluded
- Delete `plan.md` once folded in (or keep it as an archive if preferred)
- Remove or strike through anything in `spec.md` that was dropped
- Leave **Open questions** empty or delete the section

## specs/ directory

`specs/` is always a symlink into another repository (e.g. a subdirectory of a shared docs or planning repo — not necessarily its root). It must be listed in `.gitignore`. Always follow the symlink and commit spec changes in the target repository, not the project repo.

### Initializing specs/ in a project

If `specs/` doesn't exist, ask the user for the target path, then create the symlink with `python -c "import os; os.symlink('<target>', 'specs')"` and add `specs` to `.gitignore`. Never create a plain directory.

## Spec File Conventions

Specs always use a 2-level hierarchy: `specs/<area>/<feature>/`

- **area** — a coherent part of the application (e.g. `auth`, `billing`, `api`, `cli`, `infra`); use `main` if no subareas have been established yet
- **feature** — a specific capability within that area
- `spec.md` — requirements, context, decisions (long-lived)
- `test-plan.md` — coverage matrix, test data, exclusions, regression notes (long-lived, maintained alongside spec)
- Naming: kebab-case at both levels
- Optional companion files can live alongside: `research.md` (background, prior art, analysis), diagrams, mockups, etc.

## The Three Artifacts

| Artifact | Purpose | Owner | Changes when |
|---|---|---|---|
| `spec.md` | What the feature does | Product / Dev | Requirements change |
| `test-plan.md` | How it's tested, what's covered | QA / Dev | Spec changes or tests change |
| Test code (`test_*.py`) | Executable verification | Dev / QA | Implementation or spec changes |

## Checking the test plan

When reviewing or validating a `test-plan.md`, check:

1. **Every spec criterion has a row** — no acceptance criterion from `spec.md` is missing from the coverage matrix
2. **No orphan test cases** — every test case in the matrix traces to a current spec criterion
3. **Status is current** — `Covered` entries have corresponding test code that exists and passes; `Pending` entries are acknowledged
4. **Exclusions have rationale** — every item in Deliberate Exclusions explains why
5. **Test data is specified** — someone could set up the test environment from the Test Data Requirements section alone
6. **Regression notes reflect history** — if the spec has changed since initial creation, the changes are documented

## Finding WIP

```
grep -rL "## Shipped" specs/ --include="spec.md"
```

Lists all specs not yet shipped.

```
grep -c "Pending" specs/*/test-plan.md specs/*/*/test-plan.md 2>/dev/null
```

Lists test plans with uncovered criteria.

## Resources

- **`references/spec-template.md`** — minimal spec template to copy when creating a new spec
- **`references/test-plan-template.md`** — test plan template to copy when deriving tests from a spec
