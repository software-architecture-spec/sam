# SAM Roadmap

This roadmap is **feedback-driven, not predetermined**. Everything below shifts in response to issues filed, real-world authoring experience, and review from supply-chain / security / procurement practitioners. Items are ordered by current confidence, not by guaranteed delivery.

The stable target is **v1**. The path there is incremental minor releases that close gaps surfaced by real use.

## Current release: v0.2

Shipped 2026-04-26 at `https://software-architecture-spec.github.io/sam/v0.2/`.

- Specification §§1–9 (Scope, Terminology, Conformance language, Threat model, Conforming SAM, Versioning, Extensibility, Stability, SAM Levels)
- JSON Schema with §7 extensibility (`patternProperties` for `x-*`) and §8 stability annotations
- `envelope.dependencies[]` for operational third-party visibility
- Conformance test corpus (8 pass + 12 fail cases)
- Validator + CI + opt-in pre-commit hook
- `registry/standards.json` (22 entries) and `registry/tensions.json` (5 well-known IDs)

v0.1 frozen at `/sam/v0.1/` and remains valid per §6.3 same-MAJOR compatibility.

## Near-term — v0.3 candidates

These are likely to land next, **subject to feedback**. Each came from the consumer-side review of v0.2 examples that flagged gaps a procurement/security reviewer felt.

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

## Spec content still deferred from v0.2

These were named in v0.2's "Open issues" and remain on the path to v1:

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

## Explicitly out of scope

These are real concerns adjacent to SAM but **not** SAM's job:

- **DORA-specific compliance fields** — subcontractor / nth-party chain, exit/portability strategy per dependency, concentration-risk metadata, register-of-information shape. These are *contractual* and *consumer-side* concerns, not architectural facts about the subject. SAM is a quality spec, not a compliance form. `envelope.dependencies[]` gives DORA consumers the upstream architectural input they need; populating their own register is their work, not the producer's manifest format.
- **Vulnerability disclosures.** Use CSAF / VEX. SAM links to relevant security claims via `industryRefs[]` and evidence URIs.
- **License declarations.** Use SBOM (CycloneDX, SPDX) referenced via `subject.sbomRef`.
- **Build provenance.** Use SLSA / in-toto attestations as siblings to the SAM predicate.
- **Runtime telemetry.** SAM declares design intent, not observed behavior.

## How to influence the roadmap

File an issue. The [`real-world-feedback`](.github/ISSUE_TEMPLATE/real-world-feedback.md) template surfaces what's blocking actual use; the [`schema-change-proposal`](.github/ISSUE_TEMPLATE/schema-change-proposal.md) template proposes specific shape. Roadmap reordering happens in response to that input, not in advance of it.
