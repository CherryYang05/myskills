---
title: "{{PROJECT_NAME}} Architecture Baseline"
status: current
owner: "{{OWNER}}"
last_verified: {{DATE}}
related_adrs: []
---

# {{PROJECT_NAME}} Architecture

This document describes the current implemented system. ADRs preserve why it changed; Feature Specs and Roadmap describe accepted or planned behavior.

## Architecture conclusions

<!-- State the few boundaries that define the system. -->

## Scope and context

## System layers and components

| Component | Responsibility | Owned data / state | Public contracts | Hidden implementation |
|---|---|---|---|---|
|  |  |  |  |  |

## Dependency direction and invariants

### Allowed dependencies

-

### Forbidden dependencies

-

| Invariant | Why | Mechanical guard | Verification command |
|---|---|---|---|
|  |  |  |  |

## Key flows

### Flow 1

1.

## Domain terminology

| Term | Definition | Do not confuse with |
|---|---|---|
|  |  |  |

## Data, state and consistency

<!-- Ownership, event/state model, transaction boundaries, schema evolution and consistency. -->

## Failure and recovery model

<!-- Crash boundaries, retry, idempotency, partial success, unknown outcomes and recovery guarantees. -->

## Security and trust model

<!-- Untrusted inputs, permissions, secrets, isolation and threat boundaries. -->

## Runtime and deployment

<!-- Processes/services, external dependencies, topology, rollout and resource limits. -->

## Observability and operations

## Quality attributes

| Concern | Current guarantee / rule | Evidence or guard |
|---|---|---|
| Reliability / recovery |  |  |
| Security / privacy |  |  |
| Performance / resources |  |  |
| Compatibility / rollout |  |  |
| Concurrency / consistency |  |  |
| Testability / observability |  |  |

## Change protocol

Create an ADR before changing stable boundaries, dependency direction, public contracts, schema strategy, trust model, production dependencies or recovery/consistency guarantees. After implementation, synchronize the accepted outcome into this current-state document.

## Known gaps

-
