---
title: "Feature: {name}"
status: draft
feature_id: F-NNNN
milestone: null
owner: "{name}"
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
implemented_in: null
supersedes: null
superseded_by: null
related_adrs: []
---

<!--
Copy to docs/specs/F-NNNN-{slug}.md or the repository's configured Feature directory.
Delete this comment. F-NNNN is stable and must not encode milestone, release, module, or owner.
-->

# Feature: {name}

## Problem and evidence

<!-- 当前可观察问题、受影响用户/调用方、仓库证据。 -->

## Goals

- G-1:

## Non-goals

- NG-1:

## Terms and assumptions

- Term:
- Assumption:

## User scenarios and behavior

### Scenario A: {name}

- Given:
- When:
- Then:

## Functional requirements

- FR-1:

## Interfaces and contracts

<!-- CLI/API/event/file format/config/tool schema。没有变化时写 N/A + 理由。 -->

## Data, state, and migration

<!-- State transition、ownership、persistence、migration、compatibility。无状态时写 N/A + 理由。 -->

## Cross-cutting concerns

<!-- 每项写结论或 N/A + 简短理由；不要为了填表写空话。 -->

| Concern | Required semantics | Evidence / follow-up |
|---|---|---|
| Failure / partial success |  |  |
| Retry / timeout / cancellation |  |  |
| Recovery / idempotency |  |  |
| Security / trust boundary |  |  |
| Privacy / secrets |  |  |
| Observability / audit |  |  |
| Resource limits |  |  |
| Persistence / migration |  |  |
| Backward compatibility |  |  |
| Rollout / rollback |  |  |
| Concurrency / consistency |  |  |

## Architecture and coupling

- Changed public contracts:
- New or changed dependencies:
- Dependency-direction impact:
- Cycle risk:
- Code ownership / target modules:
- Mechanical guard updates:

## Alternatives and decisions

<!-- 局部取舍可留在 Spec；高代价跨模块决定引用 ADR。 -->

| Option | Benefits | Costs / failure modes | Decision |
|---|---|---|---|
|  |  |  |  |

## Acceptance criteria

<!-- 二值可判断、写可观察行为，不规定内部实现。 -->

- [ ] AC-1: When {condition}, the system shall {observable-outcome}.

## Evidence plan

| AC / risk | Planned evidence | Verification command or procedure |
|---|---|---|
| AC-1 |  |  |

## Documentation and release impact

- Engineering source of truth:
- User/developer/operations docs:
- Generated reference:
- Migration/release notes:
- No-impact rationale, if applicable:

## Open questions

- OQ-1:
