---
name: Schema change proposal
about: Propose adding, removing, or rewording a schema field, conformance rule, or spec section
title: "[schema] "
labels: ["schema", "proposal"]
---

<!--
For non-trivial schema changes, file the issue first; PRs land after discussion converges.
Please read v0.1/SPECIFICATION.md before submitting — many concerns are already addressed.
-->

## Problem

What use case isn't served by the current schema or specification? Be concrete — name the producer or consumer scenario.

## Proposed change

Specific schema diff or spec wording. If the change touches the schema, state which JSON pointer location(s).

## Alternatives considered

What other shapes did you consider? Why was the proposal above better?

## Impact on §5.1 conformance

Which conformance items does this change touch? Does it create a new conformance requirement, change an existing one, or relax one? If you're adding a new requirement, propose whether it's schema-enforceable, spec-only (like §5.1.6/7), or strict-only (like §5.1.11/12/13).

## Backward compatibility

Does this change break existing v0.1 manifests? If so, what's the migration path? Per §6.1, breaking changes are permitted in v0.x but they should be deliberate and named.

## Anchored standards

Which existing industry standards (ISO, NIST, OWASP, IETF, regulatory) inform or motivate this change? Linking to them helps reviewers evaluate whether the change is grounded.

## Additional context

Anything else — prior art in other specs (CycloneDX, SLSA, in-toto, OpenAPI), screenshots from real manifests you've authored, etc.
