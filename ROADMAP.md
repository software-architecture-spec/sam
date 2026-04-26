# SAM Roadmap

This roadmap is **feedback-driven, not predetermined**. Everything below shifts in response to issues filed, real-world authoring experience, and review from supply-chain / security / procurement practitioners. Items are ordered by current confidence, not by guaranteed delivery.

The stable target is **v1**. The path there is incremental minor releases that close gaps surfaced by real use.

## Current release: v0.1

First public draft. Live at `https://software-architecture-spec.github.io/sam/v0.1/`.

- Specification §§1–9 (Scope, Terminology, Conformance language, Threat model, Conforming SAM, Versioning, Extensibility, Stability, SAM Levels)
- JSON Schema with §7 extensibility (`patternProperties` for `x-*`) and §8 stability annotations
- `envelope.dependencies[]` for operational third-party visibility
- Conformance test corpus (8 pass + 12 fail cases)
- Validator + CI + opt-in pre-commit hook
- `registry/standards.json` (22 entries) and `registry/tensions.json` (5 well-known IDs)



## Near-term — v0.3 candidates

These are likely to land next, **subject to feedback**. Each came from an early consumer-side review of the v0.1 examples that flagged gaps a procurement/security reviewer felt.

### `envelope.serviceLevels` (service- and product-layer only)

A bucket for SLA / SLO claims that sit alongside the operational envelope:

- `availability` (e.g., "99.9%")
- `rpoMinutes`, `rtoMinutes`
- `supportWindow` (e.g., "24x7", "business-hours-EU")
- `incidentResponse` keyed by severity (critical / high / medium / low → hours-to-acknowledge)
- `vulnerabilityPatch` keyed by severity (→ days-to-fix)
- `industryRefs[]` for SOC 2 trust-criteria, ITIL, or contract-URI citations

Forbidden at `subject.layer = artifact` via `if/then` — artifacts don't have SLAs; services do.

### `intent.tenancy.dataResidency[]`

Where the subject's primary data is stored. Same shape as the existing `isolationGuarantees[]` (string array). Values: ISO 3166 codes, regional groupings ("EU"), cloud regions ("us-east-1"), or producer-defined options ("customer-selectable: EU, US"). Empty/omitted = no claim.

Tenancy is the natural home — tenancy speaks to *how* data is partitioned; residency is *where* the partitions sit. Keeping them adjacent lets consumers read both at once.

### `industryRefs[]` audit-metadata enrichment

Optional fields on each `industryRefs[]` entry:

- `auditor` — the named third party that performed the audit (e.g., "PwC", "Schellman")
- `auditPeriod` — coverage window (e.g., "2025-01-01 to 2025-12-31")
- `dateAttested` — ISO 8601 timestamp of the attestation

Closes the consumer-side gap that "SOC 2 Type 2" with no date / auditor / scope is procurement-useless.

## Spec content deferred from v0.1

These were named in v0.1's "Open issues" and remain on the path to v1:

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

## Long-horizon

- **Working-group adoption.** The `software-architecture-spec.github.io` namespace is a working-draft host. The intended long-term home is a neutral standards body (CNCF, OpenSSF, IETF SIG, or similar). Adoption depends on real-world traction, which depends on this release generating engagement.
- **Namespace migration.** When the working-group home is identified, URIs migrate with redirects so existing manifests keep resolving. This is a coordination cost, not a technical one.
- **`x-sam-stability` validation behavior.** Currently descriptive only (per §8.3). Future versions may give it semantics — e.g., consumers reject manifests that promise `stable` but use fields marked `experimental`.
- **`v1.0`.** Declared when the v0.x field set has stabilized through real use, conformance test surface is comprehensive, the canonical-strings registry has settled, and at least one working-group home has accepted the spec.

## Open questions

These came out of an early consumer-side review of the v0.1 examples. Each is either a v0.3 candidate (above) or explicitly out of scope (below) — listed here so the reasoning is visible.

- **Data residency of the subject itself.** v0.1 declares jurisdiction per dependency but not where the subject's own data lives. Consumer review flagged this as a critical DORA + GDPR Ch. V gap. *Resolution:* added as a v0.3 candidate at `intent.tenancy.dataResidency[]`.
- **Audit metadata on `industryRefs[]`.** A `SOC 2 Type 2` cite without auditor / period / date is procurement-useless. *Resolution:* v0.3 candidate.
- **SLA / SLO surface.** Incident-response SLA, vulnerability-patch SLA, MTTR/MTBF, support hours, RPO/RTO are quality claims real consumers ask for. *Resolution:* v0.3 candidate at `envelope.serviceLevels` (service- and product-layer only).
- **Subcontractor / nth-party chain per dependency.** DORA Art. 28 cares about sub-outsourcing. *Resolution:* **out of scope** — see below. SAM declares architectural facts; tracking each provider's own subcontractor chain is the consumer's compliance register, not the producer's manifest.
- **Exit / portability strategy per dependency.** Single `alternative` enum field is coarser than DORA expects. *Resolution:* **out of scope** — same rationale. The `alternative` field signals architectural substitutability; cutover plans are contractual.
- **Replaceability semantics.** Reviewer flagged `flexibility.replaceability: not_applicable` as "philosophically odd — every system has a replaceability story." *Resolution:* open. Possible v0.3 wording change in `SPECIFICATION.md` to constrain when `not_applicable` is appropriate; gathering more authoring feedback first.
- **Layer terminology clarity.** Reviewer had to infer the `artifact` / `service` / `product` hierarchy without the spec. *Resolution:* open — the layer model itself is sound; the README and authoring guide can do better at signaling the hierarchy at a glance.

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
