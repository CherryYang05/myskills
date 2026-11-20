# {{PROJECT_NAME}} repository instructions

## SDD profile

- Profile: **Complex**
- Initialized: {{DATE}}
- Owner: {{OWNER}}
- Documentation entry: [`docs/index.md`](docs/index.md)

This repository owns its daily SDD workflow. Do not invoke `develop-software` for normal Feature, bug, refactor, testing or review work.

## Read before changing code

1. Read `docs/index.md`, the Project Brief, current Architecture and Roadmap.
2. Identify the relevant accepted Feature Spec, active Implementation Plan and related ADRs.
3. Inspect the actual code, tests, generated references, current diff and repository status.
4. Treat chat as intent only; repository facts and actual evidence are authoritative.
5. Preserve user changes and exclude unrelated cleanup.

## Repository map

<!-- Replace with real directories, responsibilities, data ownership and public boundaries. -->

```text
TBD
```

## Commands

```bash
# Run / preview
TBD

# Targeted tests
TBD

# Full tests / build
TBD

# Format / lint / type check
TBD

# Architecture / schema / generated-reference checks
TBD

# SDD Artifact validation
python3 scripts/validate_sdd.py . --strict-sections
```

Only report commands actually run. State unavailable coverage and its risk explicitly.

## Source of Truth

| Fact | Authority |
|---|---|
| Project problem, users, scope and success | `docs/project/project-brief.md` |
| Milestones, ordering and exit evidence | `docs/project/roadmap.md` |
| Current components, state, dependencies and runtime boundaries | `docs/architecture/overview.md` |
| One Feature's desired observable behavior | `docs/specs/F-NNNN-*.md` |
| Long-lived architecture decision and rationale | `docs/adr/ADR-NNNN-*.md` |
| Delivery slices, progress, evidence and rollback points | `docs/plans/PLAN-F-NNNN-*.md` |
| Current implementation | Code, migrations, generated references and tests |

Do not duplicate requirements or progress between Roadmap, Spec and Plan. Accepted intent and current implementation are different facts.

## Change classification

### S0 — trivial or behavior-preserving

- Use for typo, formatting, local bug and mechanical refactor.
- Do not create ceremonial Spec, ADR or Plan.
- Add regression evidence for bugs and run risk-matched checks.
- Update current docs only when their claims changed.

### S1 — observable behavior

1. Allocate or update a stable `F-NNNN` Feature Spec.
2. Resolve requirements, failure semantics and binary acceptance criteria; keep it `draft` until owner acceptance.
3. Create `PLAN-F-NNNN` after the Spec is `accepted`; split delivery into independently verifiable vertical slices.
4. Implement one ready slice at a time and record actual evidence.
5. Close Plan and Feature only when Definition of Done is satisfied.

### S2 — architecture or high risk

Use S1 plus an ADR before implementation for changes to stable module boundaries, dependency direction, public contracts, schema/migration strategy, security/trust boundaries, production dependencies, external side-effect semantics, recovery, compatibility or consistency.

Add risk-specific tests, migration/rollout/rollback and operational evidence. A small diff does not reduce these requirements.

## Artifact governance

- Feature IDs are global, monotonic and never reused: `F-NNNN`.
- ADRs use `ADR-NNNN`; Plans use `PLAN-F-NNNN`, with `-R02` revisions only when preserving a superseded Plan.
- Feature lifecycle: `draft -> accepted -> implemented -> superseded`, or `withdrawn`.
- ADR lifecycle: `proposed -> accepted -> superseded`, or `rejected`.
- Plan lifecycle: `draft -> active -> completed`, or `abandoned` / `superseded`.
- Every active Plan references an accepted Feature; every completed Plan corresponds to an implemented Feature.
- Keep at most one active Plan per Feature. This personal-project baseline also keeps one primary Plan active repository-wide unless this file explicitly authorizes parallel work.
- Accepted ADRs preserve rationale. Supersede them instead of rewriting their meaning.
- Do not create Specs or Plans for distant backlog items; Roadmap is enough until work is selected.

## Planning and implementation

- Define slices by minimal end-to-end observable behavior, not horizontal layers.
- Associate every slice with acceptance criteria, contracts/state, tests, verification command, expected result and rollback point.
- Prefer a failing test or characterization before implementation; time-box exploratory spikes and convert retained code to production standards.
- Stop and reopen the relevant Spec/ADR/Plan when implementation exposes a semantic gap or risk escalation.
- Keep external types at adapters, enforce dependency direction, validate boundaries and place deterministic rules in tests/lint/CI.

## Safety and operations

<!-- Replace with project-specific trust, data, side-effect, compatibility and deployment boundaries. -->

- Trust and permission boundary: TBD
- Persistent data and migration rule: TBD
- External side-effect, retry and idempotency rule: TBD
- Compatibility, rollout and rollback rule: TBD
- Concurrency, consistency and resource limits: TBD
- Secrets, logging and observability rule: TBD

## Definition of Done

- All applicable acceptance criteria have sufficient actual evidence.
- Targeted, static, architecture, contract, integration and risk-specific checks pass.
- The user-visible scenario works through a real entry point where applicable.
- Plan slices, remaining work and rollback state are accurate.
- Spec, ADR, Architecture, generated references and code do not contradict one another.
- Migration, compatibility, operations, documentation and release impact are handled or explicitly not applicable.
- Artifact validator passes.
- No secret, temporary debug path, unrelated change or unowned follow-up is hidden in the diff.
