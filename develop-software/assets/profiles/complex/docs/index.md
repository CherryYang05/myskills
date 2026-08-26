# {{PROJECT_NAME}} engineering documentation

This directory is the engineering Source of Truth. Public or user-facing documentation must derive current behavior from code, tests and accepted project documents.

## Reading order

1. [Project Brief](project/project-brief.md)
2. [Current Architecture](architecture/overview.md)
3. [Roadmap](project/roadmap.md)
4. [Feature Specs](specs/README.md)
5. [Architecture Decisions](adr/README.md)
6. [Implementation Plans](plans/README.md)

## Authority map

| Question | Authority |
|---|---|
| Why does the project exist and what is out of scope? | Project Brief |
| What is delivered in which order? | Roadmap |
| How does the implemented system currently work? | Architecture + code |
| What behavior has been accepted? | Feature Spec |
| Why was a long-lived choice made? | ADR |
| What is currently being implemented and verified? | Implementation Plan |
| Does the behavior actually work? | Tests and reproducible evidence |

Current, accepted, implemented and released are different states. Chat conclusions become project facts only after entering the appropriate Artifact and version control.
