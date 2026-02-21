---
name: mspec
description: Spec-driven design workflow that keeps plans and requirements in a `specs/` directory at the project root. Do not activate automatically — only engage this workflow after the user has explicitly invoked `/mspec` in the current session. Once active, use this skill when starting a new feature, designing an API or CLI command, making a schema change, or any change that touches more than 2 files. Also handles handovers — when the user says they are taking a break, handing off, or requests a handover, update plan.md with current status and commit it.
---

# mspec

Lightweight spec-first workflow. Before implementing non-trivial changes, write or find a spec in `specs/`. After shipping, update the spec to reflect what actually happened.

## When to Write a Spec

**Always write a spec:**
- New feature, command, endpoint, or module
- Schema or data model change
- Change touching more than 2 files
- Any decision with non-obvious tradeoffs

**Skip the spec:**
- Bug fixes and typos
- Config or dependency updates
- Trivial refactors (rename, move, reformat)

## Workflow

### Starting a feature

1. Check if a spec already exists: `ls specs/` and scan for relevant area/feature directories
2. If no spec exists, identify the area and create `specs/<area>/<feature>/spec.md` using the template in `references/spec-template.md`
3. If no clear area exists yet, use `specs/main/<feature>/` as the default — refactor into named areas later as the project grows
4. Fill in **What** and **Why** at minimum — keep it to one screen
5. Show the spec to the user and get a nod before writing code

### Planning (plan mode)

When working in plan mode, write the implementation plan to `specs/<area>/<feature>/plan.md` rather than only outputting it to chat. This makes the plan shareable, reviewable, and committable before any code is written.

`plan.md` is a temporary artifact — it exists to communicate and coordinate, not to persist forever.

### During implementation

- Refer back to `spec.md` and `plan.md` when making decisions
- Add to **Decisions** in `spec.md` as choices are made
- Move unresolved items to **Open questions**

### Handover

When the user requests a handover (taking a break, switching context, handing off to someone else), update `plan.md` in place with the current status:

- Mark completed steps (e.g. with `[x]` or ~~strikethrough~~)
- Annotate the current stopping point clearly
- Note any loose context, gotchas, or decisions made during the session that aren't yet in `spec.md`
- List what to do next

Then commit `plan.md` so the state is captured in git.

### After shipping

- Fold key decisions and outcomes from `plan.md` into the **Decisions** section of `spec.md`
- Delete `plan.md` once folded in (or keep it as an archive if preferred)
- Remove or strike through anything in `spec.md` that was dropped
- Leave **Open questions** empty or delete the section

## Spec File Conventions

Specs always use a 2-level hierarchy: `specs/<area>/<feature>/`

- **area** — a coherent part of the application (e.g. `auth`, `billing`, `api`, `cli`, `infra`); use `main` if no subareas have been established yet
- **feature** — a specific capability within that area (e.g. `oauth`, `checkout`, `rate-limiting`)
- `spec.md` — requirements, context, decisions (long-lived)
- `plan.md` — implementation plan written during plan mode (temporary; delete after folding into spec)
- Naming: kebab-case at both levels
- One spec directory per feature; a spec can cover multiple related tickets
- Additional files (diagrams, mockups, research notes) can live alongside `spec.md` in the same directory

**Examples:**
```
specs/auth/oauth/spec.md
specs/billing/checkout/spec.md
specs/api/rate-limiting/spec.md
specs/cli/csv-export/spec.md
```

## Resources

- **`references/spec-template.md`** — minimal spec template to copy when creating a new spec
- **`references/plan-template.md`** — plan template to use when writing `plan.md` during plan mode
