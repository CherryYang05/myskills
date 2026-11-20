---
title: "{{PROJECT_NAME}} Project Spec"
sdd_profile: simple
status: current
owner: "{{OWNER}}"
last_verified: {{DATE}}
---

# {{PROJECT_NAME}}

This is the living product and system specification for the Simple SDD profile. Keep it concise. Separate current behavior from accepted but unimplemented behavior.

## Problem and users

- Problem:
- Primary user / caller:
- Main scenario:

## Goals

- G-1:

## Non-goals

- NG-1:

## Current behavior

<!-- Record only behavior proven by the current implementation and evidence. Empty is valid for a new project. -->

| Requirement | Observable behavior | Acceptance evidence |
|---|---|---|
| None yet | New project; no implemented behavior is claimed | Repository inspection |

## Accepted but not implemented

<!-- Move an item to Current behavior only after implementation and verification. -->

| Requirement | Scenario / acceptance criteria | Status |
|---|---|---|
| R-001 | WHEN ... THE SYSTEM SHALL ... | draft |

## Architecture sketch

<!-- Describe the current entry point, major parts, data ownership and external dependencies. Do not design hypothetical future modules. -->

```text
TBD
```

## Constraints and quality

| Concern | Required boundary or outcome | Evidence |
|---|---|---|
| Runtime / platform | TBD | TBD |
| Compatibility | TBD | TBD |
| Security / privacy | TBD | TBD |
| Performance / resources | TBD | TBD |

## Verification

| Purpose | Command or procedure | Expected result |
|---|---|---|
| Run / preview | TBD | TBD |
| Tests | TBD | TBD |
| Build / static checks | TBD | TBD |

## Backlog and open questions

- OQ-1:

## Profile upgrade triggers

Re-evaluate the SDD profile when Feature work needs independent files, architecture no longer fits a short sketch, or the project introduces stable contracts, persistent migrations, security boundaries, concurrency/recovery, multiple milestones or parallel work.
