# {{PROJECT_NAME}} repository instructions

## SDD profile

- Profile: **Simple**
- Initialized: {{DATE}}
- Owner: {{OWNER}}
- Long-term project contract: [`docs/project.md`](docs/project.md)
- Chat history is working context, never a project Source of Truth.

Use this lightweight profile while the project remains small, low risk and easy to understand as one system. Do not create Feature Spec, ADR, Plan or Roadmap directories under this profile.

## Read before changing code

1. Read `docs/project.md`.
2. Inspect the relevant implementation, tests, current diff and repository status.
3. Confirm the requested outcome, constraints and completion evidence.
4. Preserve user changes and keep unrelated cleanup out of the diff.

## Project map

<!-- Replace with the real top-level paths and purposes during initialization. -->

```text
TBD
```

## Commands

<!-- Record commands that really exist. Keep TBD explicit until the toolchain is selected. -->

```bash
# Run / preview
TBD

# Targeted test
TBD

# Full test / build
TBD

# Format / lint / type check
TBD
```

Only report checks actually run. Never convert an unavailable or failing check into “passed”.

## Daily change routing

### S0 — trivial or behavior-preserving

Use for typo, formatting, local bug fixes and mechanical refactors.

- Do not create a new SDD document.
- Reproduce bugs or add regression evidence when practical.
- Make the smallest scoped change and run targeted checks.
- Update `docs/project.md` only when observable behavior or a current project fact changed.

### S1 — observable behavior

Use for new or changed user-visible behavior.

1. Update `docs/project.md` with the proposed scenario, requirement and binary acceptance criteria under “Accepted but not implemented”.
2. Resolve material ambiguity with the owner before coding. Do not silently invent product semantics.
3. Implement the smallest end-to-end behavior and test it.
4. After evidence passes, move the behavior into “Current behavior” and update the architecture sketch if reality changed.

### S2 — architecture or high risk

Stop before implementation when the change introduces a durable public contract, data migration, permission/security boundary, irreversible external side effect, concurrency/consistency, recovery requirement, multiple deployables or long-running multi-stage delivery.

Explain why Simple is no longer sufficient and recommend rerunning `develop-software` to choose Medium or Complex. Do not improvise a partial ADR/Plan system inside Simple.

## Design and implementation rules

- Prefer the smallest design that satisfies accepted behavior.
- Keep implementation details in code; keep stable behavior, boundaries and reasons in `docs/project.md`.
- Validate untrusted input at boundaries and keep secrets out of code, logs and fixtures.
- Do not add dependencies, external writes, migrations or deployment changes without explicit approval.
- Update current facts after implementation; do not describe planned behavior as already available.

## Definition of Done

- The requested outcome and its acceptance criteria are satisfied.
- Relevant tests, build and static checks were actually run.
- `docs/project.md` agrees with observable behavior and current architecture.
- No unrelated changes, temporary debug code or secrets remain.
- Unverified scope, limitations and follow-up work are reported honestly.
