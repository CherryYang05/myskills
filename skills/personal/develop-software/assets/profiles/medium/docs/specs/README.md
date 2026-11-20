# Feature Specs

Medium Feature Specs combine requirements, technical design, delivery slices and verification evidence in one file.

Naming:

```text
docs/specs/F-NNNN-<lowercase-kebab-slug>.md
```

Rules:

- Allocate IDs monotonically and never reuse them.
- Keep a new Feature `draft` until the owner accepts its semantics.
- Do not implement a `draft` Feature.
- Mark `implemented` only when acceptance evidence and Definition of Done are complete.
- Use an ADR only for expensive, cross-Feature or hard-to-reverse decisions.
- Keep current system facts in Architecture; do not turn Feature design into current behavior before implementation.

Lifecycle:

```text
draft -> accepted -> implemented -> superseded
   \-> withdrawn
```

Create Features from [`../templates/feature-spec.md`](../templates/feature-spec.md).

## Index

<!-- Add one row when a real Feature is created. -->

| Feature | Status | Outcome |
|---|---|---|
| None yet | — | — |
