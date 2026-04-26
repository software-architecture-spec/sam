# SAM Roadmap

This roadmap is **feedback-driven, not predetermined**. Everything below shifts in response to issues filed, real-world authoring experience, and review from supply-chain / security / procurement practitioners. Items are ordered by current confidence, not by guaranteed delivery.

The stable target is **v1**. The path there is incremental minor releases that close gaps surfaced by real use.

## Current release: v0.2

Live at `https://software-architecture-spec.github.io/sam/v0.2/`.

- Specification §§1–10 (Scope, Terminology, Conformance language, Threat model, Conforming SAM, Versioning, Extensibility, Stability, SAM Levels, **Definitions appendix**)
- JSON Schema with `envelope.serviceLevels`, `intent.tenancy.dataResidency[]`, and `industryRefs[]` audit metadata (auditor / auditPeriod / dateAttested)
- Open-content definitions in §10 covering all 9 ISO 25010 characteristics and ~40 sub-characteristics — SAM is now usable without paywalled ISO access
- Conformance corpus extended (positive + negative cases for the new fields)

v0.1 frozen at `/sam/v0.1/` and remains valid per §6.3 same-MAJOR compatibility.

## Shipped in v0.2

These were the v0.2 candidates carried forward from the v0.1 review and now in the schema:

- **Definitions appendix** (`SPECIFICATION.md §10`) — all 9 ISO 25010 characteristics and 40 sub-characteristics defined in our own CC-BY-4.0 wording with example producer claims. Closes the paywalled-ISO gap.
- **`envelope.serviceLevels`** (service/product-layer only; `if/then` enforces) — `availability`, `rpoMinutes` / `rtoMinutes`, `supportWindow`, `incidentResponse` keyed by severity, `vulnerabilityPatch` keyed by severity, `industryRefs[]`.
- **`intent.tenancy.dataResidency[]`** — string array; ISO 3166 codes, regional groupings, cloud regions, or producer-defined options.
- **`industryRefs[]` audit-metadata enrichment** — optional `auditor`, `auditPeriod`, `dateAttested` on every `industryRefs` entry (qualityAttributes claims, dependencies, serviceLevels).
- **Recommended open references** (`§1.5`) — Wikipedia ISO 25010, arc42 quality model, NIST SP 800-160 Vol. 1 as informational broadening for readers who want context beyond the §10 definitions.

## Near-term — v0.3 candidates

Drawn from a review of canonical systems-design literature (Release It! / DDIA / Fowler PEAA / SRE Book / Newman / Richards & Ford / Ousterhout) — each names a vocabulary producers and consumers commonly use that SAM has no slot for today.

### `architecturalStyle` (declarative)

Single-value enum on `intent` declaring the architectural style:

`monolith | modular_monolith | microservices | serverless | event_driven | actor | hybrid`

Producers can scope their claims; consumers can match the style against their target architecture. Distinct from `subject.layer` (granularity of *this* manifest) and from `subject.components[]` (composition).

### `architecturalPatterns[]` + `registry/patterns.json`

A new array on `qualityAttributes.*.overall` (or top-level `architecturalPatterns[]` — to be decided) for declaring named patterns the software implements:

```
[
  { "id": "circuit_breaker", "appliesTo": ["dependencies", "reliability"] },
  { "id": "cqrs", "appliesTo": ["data"] },
  { "id": "cache_aside", "appliesTo": ["performance"] }
]
```

Companion `registry/patterns.json` (same shape as `tensions.json`) seeds canonical IDs from Release It! (`circuit_breaker`, `bulkhead`, `timeout`, `fail_fast`, `retry_with_backoff`, `fallback`), DDIA (`event_sourcing`, `cqrs`, `saga`, `outbox`), Fowler PEAA (`unit_of_work`, `repository`), and caching literature (`cache_aside`, `write_through`, `write_back`).

Closes the gap that producers can't declare "this implements the circuit-breaker pattern" or "this is event-sourced" — vocabulary every senior engineer expects to see.

### Storage architecture detail

`envelope.persistence` today is a `stores[]` enum (`sql`, `kv`, `document`, `blob`, `search`, `queue`, `filesystem`, `other`). v0.3 candidates: replication topology (single / primary-replica / multi-primary / sharded), consistency model (strong / read-after-write / eventual), backup posture (none / snapshot / continuous), encryption posture (at-rest / in-flight / both).

### Concurrency-model detail

`envelope.instantiation.mode` today covers singleton / multi_instance / leader_elected / sharded. v0.3 candidates: ordering guarantees (none / per-key / total), idempotency claims, conflict-resolution model (last-write-wins / CRDT / application-defined).

## Spec content deferred from v0.2

Carried forward unchanged into v0.3+:

- **Authoring guide** — practical guidance for producers on what to populate per attribute and how to write honest summaries.
- **Verification guide** — practical guidance for consumers on how to evaluate a SAM in different decision contexts.
- **Lifecycle policy** — re-issuance, revocation, supersession.
- **Subject-aware DSSE binding for non-artifact layers** — service- and product-layer manifests have optional `subject.digest`; binding without a content-addressed digest is currently underspecified.

These are prose-heavy and depend on observed authoring patterns. They'll land once we have enough real manifests to learn from.

## Tooling

- **Spec-aware validator** — a reference implementation that catches the spec-only conformance items the JSON Schema can't enforce: §5.1.6 (`evidence` required when `status: verified`), §5.1.7 (`summary` required when `status: declared|verified`), §5.1.9 (interpretable `industryRefs.standard`), §5.1.11 (well-known or `x:`-prefixed `tensionsDeclared.tension`). The conformance corpus already exercises these; what's missing is the validator that consumes the corpus.
- **Authoring assistance** — once the authoring guide exists, lightweight tooling that walks an artifact / service / product and produces a SAM scaffold from build metadata (SBOM, CI config, runtime configuration) for the producer to refine.

## Registries

- **Growth of `standards.json`** — community contributions adding aliases and new entries as real SAMs cite standards we haven't seen yet.
- **Governance model** — when a new standard is added, who decides the canonical spelling? The current advisory-not-enforced status keeps the cost low; if/when we reach working-group adoption the model formalizes.
- **`registry/patterns.json`** — seeded in v0.3 alongside `architecturalPatterns[]`.

## Long-horizon

- **Working-group adoption.** The `software-architecture-spec.github.io` namespace is a working-draft host. The intended long-term home is a neutral standards body (CNCF, OpenSSF, IETF SIG, or similar). Adoption depends on real-world traction, which depends on this release generating engagement.
- **Namespace migration.** When the working-group home is identified, URIs migrate with redirects so existing manifests keep resolving. This is a coordination cost, not a technical one.
- **`x-sam-stability` validation behavior.** Currently descriptive only (per §8.3). Future versions may give it semantics — e.g., consumers reject manifests that promise `stable` but use fields marked `experimental`.
- **`v1.0`.** Declared when the v0.x field set has stabilized through real use, conformance test surface is comprehensive, the canonical-strings registry has settled, and at least one working-group home has accepted the spec.

## Open questions

These came out of consumer-side review and design-pattern coverage analysis. Each is either resolved (above), v0.3 candidate (above), or out-of-scope (below) — listed here so the reasoning is visible.

**Resolved in v0.2:**

- ✅ **Data residency of the subject itself** — landed as `intent.tenancy.dataResidency[]`.
- ✅ **Audit metadata on `industryRefs[]`** — landed as optional `auditor` / `auditPeriod` / `dateAttested` fields.
- ✅ **SLA / SLO surface** — landed as `envelope.serviceLevels` (service/product layer only).
- ✅ **ISO 25010 paywall dependency** — closed via `SPECIFICATION.md §10` definitions appendix and §1.5 open companions. SAM is now usable from §10 alone without paywalled ISO access.

**Open / v0.3 candidates:**

- **Architectural style declaration.** Reviewer noted SAM has no slot for "this is event-sourced microservices" — common shorthand vocabulary. *Proposed:* `intent.architecturalStyle` enum.
- **Pattern catalog.** Canonical patterns from Release It! / DDIA / Fowler PEAA / caching literature aren't nameable in SAM today. *Proposed:* `architecturalPatterns[]` + `registry/patterns.json`.
- **Storage architecture detail.** `envelope.persistence` is thin; reviewers want replication topology, consistency model, backup posture. *Proposed:* expand `envelope.persistence` for v0.3.
- **Concurrency-model detail.** `envelope.instantiation.mode` is thin; reviewers want ordering guarantees, idempotency, conflict resolution. *Proposed:* expand `envelope.instantiation` for v0.3.

**Open / no decision yet:**

- **Replaceability semantics.** Reviewer flagged `flexibility.replaceability: not_applicable` as "philosophically odd — every system has a replaceability story." Possible v0.3 wording change in `SPECIFICATION.md §10.8` to constrain when `not_applicable` is appropriate; gathering more authoring feedback first.
- **Layer terminology clarity.** Reviewer had to infer the `artifact` / `service` / `product` hierarchy without the spec. The model itself is sound; the README and authoring guide can do better at signaling the hierarchy at a glance.

**Explicitly out of scope (carried forward):**

- **Subcontractor / nth-party chain per dependency.** DORA Art. 28 cares about sub-outsourcing. SAM declares architectural facts; tracking each provider's own subcontractor chain is the consumer's compliance register, not the producer's manifest.
- **Exit / portability strategy per dependency.** Single `alternative` enum field is coarser than DORA expects. The `alternative` field signals architectural substitutability; cutover plans are contractual.
- **IEEE / ACM as a parallel quality-model anchor.** Investigated. IEEE Std 1061 (Software Quality Metrics Methodology) was withdrawn in 2018; ACM doesn't publish quality-model standards; ISO 25010 has near-monopoly recognition. SAM stays anchored to ISO 25010 names with open CC-BY-4.0 definitions in §10. No need for a "spin #2" in IEEE/ACM.

## Explicitly out of scope

SAM is an **architectural visibility framework**, not a compliance framework. The line below isn't a refusal of compliance use cases — it's a refusal of letting compliance use cases dictate the shape of the architectural surface. Consumers under any specific regime read SAM to populate their own compliance artifacts; SAM's job is the architectural input layer that survives every regime simultaneously.

These are real concerns adjacent to SAM but **not** SAM's job:

- **Compliance form-filling for any specific regime.** DORA Art. 28 third-party register entries, NIS2 essential / important classifications, SOC 2 control narratives, HIPAA security risk assessments, FedRAMP SSP sections — all consumer-side artifacts that SAM helps populate but does not itself replace.
- **Subcontractor / nth-party chain per dependency.** Producer declares dependencies; consumer reasons about sub-outsourcing.
- **Exit / portability strategy per dependency.** Contractual surface, not architectural.
- **Concentration-risk metadata.** Cross-vendor consumer concern; impossible for any single producer to declare.
- **Vulnerability disclosures.** Use CSAF / VEX. SAM links to relevant security claims via `industryRefs[]` and evidence URIs.
- **License declarations.** Use SBOM (CycloneDX, SPDX) referenced via `subject.sbomRef`.
- **Build provenance.** Use SLSA / in-toto attestations as siblings to the SAM predicate.
- **Runtime telemetry.** SAM declares design intent, not observed behavior.

## How to influence the roadmap

File an issue. The [`real-world-feedback`](.github/ISSUE_TEMPLATE/real-world-feedback.md) template surfaces what's blocking actual use; the [`schema-change-proposal`](.github/ISSUE_TEMPLATE/schema-change-proposal.md) template proposes specific shape. Roadmap reordering happens in response to that input, not in advance of it.
