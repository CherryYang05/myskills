# Feature Specs

Feature Specs define desired observable behavior, scope, failure semantics and acceptance criteria. They do not store implementation progress.

Naming:

```text
docs/specs/F-NNNN-<lowercase-kebab-slug>.md
```

Lifecycle:

```text
draft -> accepted -> implemented -> superseded
   \-> withdrawn
accepted -> draft    # explicit reopen before implementation
```

Rules:

- Allocate IDs monotonically and never reuse them.
- Do not encode milestone, module, owner or release into the ID.
- Do not implement a draft Feature.
- Mark implemented only when its Plan, evidence and Definition of Done are complete.
- Use [`../templates/feature-spec.md`](../templates/feature-spec.md) for real, selected work; do not create empty Specs for the full Roadmap.

## Index

| Feature | Status | Milestone | Outcome |
|---|---|---|---|
| None yet | — | — | — |
