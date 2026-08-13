# {{PROJECT_NAME}} repository instructions

## SDD profile

- Profile: **Medium**
- Initialized: {{DATE}}
- Owner: {{OWNER}}
- Project scope: [`docs/project/project-brief.md`](docs/project/project-brief.md)
- Current architecture: [`docs/architecture/overview.md`](docs/architecture/overview.md)
- Feature index: [`docs/specs/README.md`](docs/specs/README.md)
- Decision index: [`docs/adr/README.md`](docs/adr/README.md)

This repository owns its workflow. Do not invoke `develop-software` for normal Feature, bug, refactor, test or review work.

## Read before changing code

1. Read the Project Brief and current Architecture.
2. Read the relevant Feature Spec and related ADRs.
3. Inspect the actual code, tests, current diff and repository status. Chat history is not a Source of Truth.
4. Preserve user changes and keep unrelated cleanup outside the task.

## Repository map

<!-- Replace with real directories, responsibilities and ownership during initialization. -->

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

# Documentation / architecture checks
TBD
```

Only report commands actually run. State missing verification and its risk explicitly.

## Source of Truth

| Fact | Authority |
|---|---|
| Product problem, goals, non-goals, near-term milestones | `docs/project/project-brief.md` |
| Current module, data and runtime boundaries | `docs/architecture/overview.md` |
| One Feature's behavior, design, delivery slices and evidence | `docs/specs/F-NNNN-*.md` |
| Cross-Feature, expensive or hard-to-reverse decisions | `docs/adr/ADR-NNNN-*.md` |
| Current implementation | Code, migrations, generated references and tests |

Do not copy the same status or requirement into multiple authorities.

## Change routing

### S0 — trivial or behavior-preserving

- Use for typo, formatting, local bug and mechanical refactor.
- Do not create a Feature Spec or ADR by default.
- Add regression evidence for bugs and run targeted checks.
- Update current docs only when their claims changed.

### S1 — observable behavior

1. Allocate the next stable `F-NNNN` and create `docs/specs/F-NNNN-<slug>.md` from the template.
2. Define problem, Goals, Non-goals, scenarios, requirements and binary acceptance criteria.
3. Record the technical design and independently verifiable delivery slices in the same Feature file.
4. Keep the Feature `draft` until the owner accepts its actual semantics; do not implement a draft.
5. Implement one ready slice at a time, record real evidence, then mark the Feature `implemented` only after DoD.

### S2 — architecture or high risk

Use S1 plus an ADR before implementation when changing module/dependency direction, public contracts, schema strategy, security/trust boundary, production dependencies, external side-effect semantics or another expensive cross-Feature decision.

If recovery, consistency, irreversible data, multi-deployable rollout, parallel Feature delivery or many cross-Artifact relations become recurring concerns, stop and recommend recalibrating to Complex instead of stretching Medium indefinitely.

## Artifact rules

- Feature IDs are global, monotonic and never reused; milestone or module changes do not change the ID.
- Feature lifecycle: `draft -> accepted -> implemented -> superseded`, with `withdrawn` for abandoned work.
- ADR lifecycle: `proposed -> accepted -> superseded`, with `rejected` for declined decisions.
- Accepted ADRs preserve rationale; replace semantic changes with a superseding ADR.
- Keep design and delivery slices in the Feature Spec. Do not create an independent Plan directory under Medium.
- Do not create an ADR for ordinary implementation choices or a Feature file for formatting-only work.

## Architecture and safety

- Preserve documented dependency direction and component responsibilities.
- Validate untrusted inputs and translate external types at boundaries.
- Define timeout, retry, idempotency, migration, compatibility and rollback when applicable.
- Keep secrets out of code, logs, fixtures and documentation.
- Convert enforceable rules into tests, lint, schema checks or CI.

## Definition of Done

- All applicable acceptance criteria have actual evidence.
- Targeted tests and repository-required broader checks pass.
- Delivery slices and remaining work are accurate.
- Architecture, ADR, user/developer docs and generated references match the implementation.
- Migration, rollback, security, compatibility and release impact are handled or explicitly not applicable.
- No unrelated change, temporary debug path, secret or unused abstraction remains.
