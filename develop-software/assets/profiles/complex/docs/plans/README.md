# Implementation Plans

Plans store the delivery strategy, independently verifiable vertical slices, current progress, evidence and rollback points for an accepted Feature.

Naming:

```text
docs/plans/PLAN-F-NNNN-<lowercase-kebab-slug>.md
docs/plans/PLAN-F-NNNN-R02-<slug>.md  # only when preserving a superseded Plan
```

Lifecycle:

```text
draft -> active -> completed
               \-> abandoned
               \-> superseded
```

Rules:

- A Plan references an existing accepted Feature before becoming active.
- Keep at most one active Plan per Feature and follow the repository WIP limit in `AGENTS.md`.
- A completed Plan has no pending required slice or verification result.
- Complete the Plan and mark the Feature implemented in the same closing change.
- Create Plans from [`../templates/implementation-plan.md`](../templates/implementation-plan.md).

## Active

- None.

## Completed

- None.
