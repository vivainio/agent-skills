---
name: mspec
description: "Spec-driven design workflow keeping plans and requirements in a `specs/` directory. Never activates automatically — only engages after explicit `/mspec` invocation. Also handles handovers: when the user requests one, update `plan.md` with current status and commit it."
---

# mspec

## Workflow

### Starting a feature

1. Check if a spec already exists: `ls specs/` and scan for relevant area/feature directories
2. If no spec exists, identify the area and create `specs/<area>/<feature>/spec.md` using the template in `references/spec-template.md`
3. If no clear area exists yet, use `main` as the area (see Spec File Conventions)
4. Fill in **What** and **Why** at minimum — keep it to one screen
5. Show the spec to the user and get a nod before writing code

### During implementation

- Add to **Decisions** in `spec.md` as choices are made
- Move unresolved items to **Open questions**

### Handover

When the user requests a handover, write `plan.md` capturing current status: what's done, where things stopped, any loose context or decisions not yet in `spec.md`, and what to do next. Then commit it.

### After shipping

- Fold key decisions and outcomes from `plan.md` into the **Decisions** section of `spec.md`
- Fill in the **Shipped** section with the commit or PR reference and date
- Delete `plan.md` once folded in (or keep it as an archive if preferred)
- Remove or strike through anything in `spec.md` that was dropped
- Leave **Open questions** empty or delete the section

## specs/ directory

The `specs/` directory at the project root is probably a symlink to a location in another repository (e.g. a shared docs or planning repo), and should be listed in `.gitignore`. Follow the symlink and commit spec changes in the target repository, not the project repo.

### Initializing specs/ in a project

If `specs/` doesn't exist, ask the user for the target path, then create the symlink with `python -c "import os; os.symlink('<target>', 'specs')"` and add `specs` to `.gitignore`. Never create a plain directory.

## Spec File Conventions

Specs always use a 2-level hierarchy: `specs/<area>/<feature>/`

- **area** — a coherent part of the application (e.g. `auth`, `billing`, `api`, `cli`, `infra`); use `main` if no subareas have been established yet
- **feature** — a specific capability within that area
- `spec.md` — requirements, context, decisions (long-lived)
- Naming: kebab-case at both levels
- Optional companion files can live alongside `spec.md`: `research.md` (background, prior art, analysis), `testing.md` (test strategy, edge cases), diagrams, mockups, etc.

## Finding WIP

```
grep -rL "## Shipped" specs/ --include="spec.md"
```

Lists all specs not yet shipped.

## Resources

- **`references/spec-template.md`** — minimal spec template to copy when creating a new spec
