---
title: "System Design: {project}"
status: current
owner: "{name}"
last_verified: YYYY-MM-DD
related_adrs: []
---

<!--
Copy to docs/architecture/system-design.md or the repository's current-state architecture location.
Delete this comment. Keep this document synchronized with current accepted architecture; use ADRs for history.
-->

# System Design: {project}

## Scope and context

<!-- 本文覆盖哪些系统边界？哪些相邻系统明确不覆盖？ -->

## Architecture overview

<!-- 一段话和一张必要的 component/flow 图，让新 Agent 快速建立 current-state 心智模型。 -->

## Components and ownership

| Component | Responsibility | Owned data/state | Public contracts | Hidden implementation |
|---|---|---|---|---|
|  |  |  |  |  |

## Dependency direction and invariants

### Allowed dependencies

-

### Forbidden dependencies

-

### Architecture invariants

| Invariant | Why it exists | Mechanical guard | Verification command |
|---|---|---|---|
|  |  |  |  |

## Key flows

### Flow 1: {observable-flow}

1.
2.

## Data, state, and consistency

<!-- Ownership、transaction/atomic boundary、schema evolution、consistency model。无持久状态时写 N/A + 理由。 -->

## Runtime and deployment boundaries

<!-- process/service topology、external dependencies、trust boundary、resource limits。 -->

## Cross-cutting quality model

| Concern | Current rule / guarantee | Evidence or guard |
|---|---|---|
| Failure / recovery |  |  |
| Security / privacy |  |  |
| Observability |  |  |
| Performance / resources |  |  |
| Compatibility / rollout |  |  |
| Concurrency / consistency |  |  |

## Change protocol

<!-- 哪些变化必须先有 ADR？哪些文档/guard 随变化同步？ -->

## Known gaps

<!-- 只写当前架构已知限制，future work 链接 Roadmap/Feature，不伪装成当前能力。 -->

-
