# {Project} repository instructions

<!--
Use this as source material during one-time workflow initialization.
Replace every placeholder, remove unused sections, and preserve established repository conventions.
Keep this file self-contained for ordinary work; do not require agents to invoke develop-software again.
Do not store current Feature progress here.
-->

## Project context

- Purpose:
- Current stage:
- Primary users / callers:
- Authoritative project scope:

## Read before changing code

- Read the nearest applicable repository instructions before editing.
- Read the relevant current architecture, roadmap, accepted behavior contract, decision, and active plan:
- Inspect current code, tests, generated references, `git status`, and the existing diff. Chat history is not a project source of truth.
- Preserve user changes and keep unrelated cleanup out of the task.
- Keep unverified project facts as assumptions or open questions; do not invent owners, supported versions, deadlines, guarantees, or approvals.

## Repository map

```text
{path}  # purpose / ownership
```

## Build and verification commands

```bash
# Build / run / preview
{build-command}

# Targeted test
{targeted-test-command}

# Full or broader test
{full-test-command}

# Format / lint / type / compile
{static-check-command}

# Architecture / schema / generated-reference / docs guards
{boundary-check-command}
```

Only report commands actually run. If a required check cannot run, state the missing coverage and risk.

## Change routing

<!--
Adapt this table to the workflow modules selected for the project.
Replace Feature Spec with issue/RFC when that is the project's chosen source of truth.
-->

| Change | Required before implementation | Required evidence / closeout |
|---|---|---|
| Mechanical, behavior-preserving, local | Confirm scope; no new Artifact by default | Targeted checks; no unrelated refactor |
| Observable behavior or public contract | Update the project's behavior contract and acceptance criteria | AC-to-evidence mapping and affected docs |
| Architecture or high-risk boundary | Resolve the decision and rollback path before coding | Risk-specific tests, architecture checks, current-state docs |
| Multi-slice, cross-session, migration or rollout | Create/update the project's active implementation plan | Slice evidence, remaining work and rollback point |

Security, persistence/migration, external side effects, public compatibility, concurrency/consistency and production dependencies always trigger explicit risk review even when the diff is small.

## Artifact policy

- Enabled behavior-contract source and location:
- Stable Feature IDs: enabled / disabled; allocation rule:
- ADR threshold and location:
- Independent Plan threshold and location:
- Roadmap and current architecture locations:
- Approval/state-transition owners:
- Validator command, if enabled:

Do not create empty Specs, ADRs or Plans. Do not duplicate status or requirements across roadmap, plan and behavior contract.
Creating an Artifact does not accept it. Keep new contracts and decisions in their initial state until the authorized owner accepts their actual content.

## Architecture invariants

| Invariant | Applies to | Mechanical guard / review Gate |
|---|---|---|
|  |  |  |

## Safety, data, compatibility and operations

- Trust and permission boundary:
- Persistent data / migration rule:
- External side effects / retry / idempotency rule:
- Compatibility and rollout rule:
- Concurrency / consistency / resource-limit rule:
- Secrets, logging and observability rule:

## Documentation sources of truth

| Fact | Authoritative location | Update trigger |
|---|---|---|
| Project scope |  |  |
| Current architecture |  |  |
| Planned outcomes |  |  |
| Accepted behavior |  |  |
| Decisions |  |  |
| Active implementation state |  |  |
| User / operator behavior |  |  |

## Definition of Done

- The requested observable outcome and applicable acceptance criteria are satisfied.
- Risk-matched tests and repository-required checks were actually run.
- Architecture, generated references and current-state docs agree with the implementation.
- Migration, compatibility, rollout/rollback, operations and documentation impact are handled or explicitly not applicable.
- No secret, temporary debug path, unrelated change or unowned follow-up is hidden in the diff.
- Remaining work, unverified scope and known limitations are reported accurately.

## Prohibited changes without explicit approval

-
