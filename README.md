# Software Architecture Manifest (SAM)

A producer-signed, machine-readable declaration of what software was designed to do and the operational envelope it was designed for.

SBOM tells you what's inside the software. SLSA tells you how it was built. OpenSSF Scorecard tells you whether good practices were followed. **SAM tells you what the producer designed it to be.**

> A nutrition label for architecture, signed by the maintainer, shipped on every artifact.

> **Working draft — not adoption-ready.** SAM is a v0 working proposal. Breaking changes are still possible (per `SPECIFICATION.md §6.1`); the stable target is v1. We are publishing this draft to gather technical review and contributors, *not* to declare a finished standard. If you operate SAMs in production today, you are early — please file feedback. **What we're asking for:** technical review of the schema and spec from supply-chain, security, and procurement practitioners; real-world authoring feedback (what's hard, what's missing); citations and registry contributions; implementations of the spec-aware validator surface (§5.1.6, §5.1.7, §5.1.9, §5.1.11). See [CONTRIBUTING.md](CONTRIBUTING.md), [ROADMAP.md](ROADMAP.md), and the [issue templates](.github/ISSUE_TEMPLATE/).

The current version is **v0.2**. v0.1 is frozen at [`/sam/v0.1/`](sam/v0.1/) and remains accessible at its URIs (per `SPECIFICATION.md §6.3`, same-MAJOR backward compatibility).

> **Normative reference.** The [SPECIFICATION.md](sam/v0.2/SPECIFICATION.md) document is the normative source for what a conforming SAM is and means. The JSON Schema in this repo is the syntactic form; the specification defines what conformance to that form requires. §§1–9 are written: Scope, Terminology, Conformance language, Threat model, Definition of a conforming SAM, Versioning, Extensibility, Stability, **SAM Levels (L0–L3)**. Authoring guide, verification guide, and lifecycle policy are deferred.

> **Note on the namespace.** The schema's `$id` (`https://software-architecture-spec.github.io/sam/v0.2/schema.json`) is hosted on GitHub Pages under the `software-architecture-spec` org. For SAM to become a useful cross-vendor standard, the namespace should eventually live with a neutral host (e.g., a CNCF / OpenSSF / IETF working group). The current host is appropriate for a working draft; URIs will redirect when the namespace moves.

---

## Why

In the AI era, a vibe-coded weekend prototype and a hardened production service are visually indistinguishable: same React frontend, same Postgres, same Dockerfile, same deployment pipeline. The Access database on a shared drive used to advertise its own fragility. The modern equivalent does not.

SAM restores that signal. A manifest that honestly declares `audience: single_user`, `scaling: none`, `observability: unspecified`, `tenancy: none` *is* the modern `.mdb` file announcing what it is — without the ambiguity of inference from stack choices.

---

## Layers — what a manifest describes

The same questions ("how does it scale", "what privilege does it run with", "is it multi-tenant") get different answers at three different layers, read by three different audiences. A SAM declares its layer explicitly via `subject.layer`:

| Layer | Granularity | Audience | Notes |
|---|---|---|---|
| `artifact` | one container image, binary, or package | AI agents, build/SLSA, SBOM tooling | The signing granularity. `digest` is required. Matches in-toto subject convention. |
| `service` | a logical SLO-owning unit (1+ artifacts) | SRE, on-call, ops | Where SLOs and incident response actually live. `digest` optional; uses `components[]` to point at constituent artifact SAMs. |
| `product` | the contractual / customer-facing surface | Procurement, audit, customers | What gets sold. `components[]` points at constituent service SAMs. |

A small project may only need one SAM at the `artifact` layer. A real product typically has all three, with each layer's manifest referencing its constituents via `subject.components[]`. Composition is explicit; nothing is inferred.

## Levels — how much a manifest tells you (new in v0.2)

A SAM is either conforming or it isn't. But producers and consumers also need a vocabulary for how *much* a SAM tells them. SAM Levels (`SPECIFICATION.md §9`) define four tiers:

| Level | Meaning | Audience cost | Compliance posture |
|---|---|---|---|
| **L0** | No SAM exists | n/a | Reverse-engineering required |
| **L1** | Conforming SAM (per §5.1) is signed and bound to its subject | Moderate intake | Initial evaluation possible |
| **L2** | L1 + every non-trivial claim has `industryRefs[]` | Auditor automation | Sufficient for many third-party-risk processes |
| **L3** | L2 + every `verified` claim has `evidence[]`; tensions are declared; `validFor` is current | Maps to strict conformance | Substantially substitutes for direct due-diligence in regulated contexts |

Levels are about *evaluability*, not *quality*. An L3 manifest declaring "P95 latency is 30 seconds" is L3-conforming; whether 30 seconds is acceptable is a consumer judgment outside SAM's scope.

## Structure (v0.2)

```
manifest
├── manifestVersion          schema version (v0.2)
├── subject                  what this manifest describes
│   ├── layer                artifact | service | product (granularity declaration)
│   ├── name, version
│   ├── digest               required at layer=artifact, optional at service/product
│   ├── sbomRef              optional pointer to SBOM
│   └── components[]         lower-layer subjects (for service/product manifests)
├── intent                   purpose, audience, tenancy, out-of-scope
├── envelope                 operational design target (the "what was it built for")
│   ├── throughput           target/max RPS, latency SLOs, concurrency
│   ├── scaling              axis (horizontal/vertical/none), statefulness
│   ├── instantiation        singleton / multi_instance / leader_elected / sharded
│   ├── privilege            root_required / unprivileged / capability_scoped
│   ├── network              isolated / egress_only / ingress_only / bidirectional
│   ├── dependencies[]       third-party ICT services this software runs against (DORA / NIS2 / 27036 / 800-161)
│   └── persistence          required stores
├── qualityAttributes        ISO/IEC 25010:2023 — 9 characteristics + sub-characteristics
├── extensions               quality concerns ISO 25010 doesn't cover cleanly
│   ├── observability        (folds awkwardly under maintainability.analysability)
│   ├── dataLifecycle        retention, deletion, archival
│   └── internationalization
├── tensionsDeclared         which side of CAP/observability-cost/etc. did you pick?
└── producer                 issuer + contact + issuedAt + validFor

x-* extension keys are permitted on:
  qualityAttributeClaim, qualityAttributes characteristic objects,
  tensionsDeclared[] items, industryRefs[] items, evidence[] items,
  producer, subject.components[] items.
```

### Claim status

Every quality attribute claim has one of four statuses:

- `unspecified` — the producer makes no claim. (Honest absence is better than fake assurance.)
- `declared` — the producer asserts but provides no evidence. (Take their word for it.)
- `verified` — the producer asserts and points to evidence (load test, security scan, audit, CI run).
- `not_applicable` — the producer claims this attribute is irrelevant for this artifact.

This three-track model (declared / verified / unspecified) mirrors how SBOM standards grew attestation lanes over time. v0.x is friendly to declared-only manifests; v1 will define stricter attestation requirements for the `verified` track. SAM Levels (§9) layer on top of these statuses to express how much of the manifest is anchored and evidenced.

---

## Standards alignment

SAM uses two reference layers per claim:

- **`industryRefs[]`** — *normative*. Industry-standard anchors that auditors and procurement teams recognize. First-class on the manifest because they outlive any single host or vendor.
- **`informationalRefs[]`** — *non-normative*. https URIs to design-context resources (pattern catalogs, internal docs, knowledge bases) that aided the producer's reasoning. Useful for AI agents and humans who want to drill into rationale; not anchors an auditor relies on.

### Top-level standards

| Layer | Standard | Where it lives |
|---|---|---|
| Software supply chain (contents) | SBOM (CycloneDX / SPDX) | `subject.sbomRef` |
| Build provenance | SLSA / in-toto | external attestation; SAM is a sibling predicate |
| Quality model spine | **ISO/IEC 25010:2023** | `qualityAttributes` keys = the 9 characteristics |
| Operational third-party risk | EU DORA Art. 28, NIS2, ISO/IEC 27036, NIST SP 800-161 | `envelope.dependencies[]` |

### Per-section industry anchors (use as `industryRefs[]`)

| Section | Recommended anchors |
|---|---|
| `qualityAttributes.security.*` | NIST SP 800-218 (SSDF), OWASP ASVS L1/L2/L3, ISO/IEC 27001, SOC 2, NIST SP 800-53, **CIS Benchmarks**, **NIST SP 800-190** (containers) |
| `qualityAttributes.interactionCapability.inclusivity` | WCAG 2.2 (A / AA / AAA), EN 301 549, Section 508 |
| `qualityAttributes.compatibility.interoperability` | OpenAPI 3.x, AsyncAPI, SCIM, SAML, OAuth 2.x, OIDC |
| `qualityAttributes.flexibility.installability` | OCI Image Spec, Helm chart schema |
| `qualityAttributes.safety` (domain-specific) | ISO 26262 (automotive), IEC 62304 (medical), DO-178C (aviation), IEC 61508 (industrial) |
| `qualityAttributes.functionalSuitability` | ISO/IEC 25010:2023 (correctness/completeness/appropriateness) |
| `envelope.dependencies[]` | EU DORA Art. 28, NIS2, ISO/IEC 27036, NIST SP 800-161 |
| `extensions.observability` | OpenTelemetry semantic conventions |
| `extensions.dataLifecycle` | ISO/IEC 25012, GDPR articles, CCPA, HIPAA, SOX §802, PCI DSS, **NIST SP 800-88 Rev. 1** (deletion side) |
| `extensions.internationalization` | Unicode CLDR, ICU MessageFormat, BCP 47 |
| Build / supply chain (top-level) | SLSA build level (L0–L3, where L0 = no claim), in-toto attestation, CycloneDX/SPDX |

These are starting points, not an exhaustive list. Producers populate `industryRefs[]` with whatever standards their audit/procurement context actually recognizes. The schema does not constrain the `standard` field to an enum; the `/registry/standards.json` companion artifact provides canonical spellings as advisory guidance.

### Why ISO 25010, but not only

ISO 25010:2023 was adopted as the canonical key set for `qualityAttributes` because it is the formal quality model that procurement, audits, and certifications already speak. Producers can populate the `overall` claim per characteristic for a coarse manifest, or drill into `subCharacteristics` for a granular one.

ISO 25010 has gaps. Observability has no first-class home (it folds under `maintainability.analysability`); data lifecycle and i18n have no formal home at all. These live in `extensions`.

The operational `envelope` (tenancy, instantiation mode, privilege, network posture, dependencies) is intentionally not part of `qualityAttributes` — these are deployment/operational signals, not quality claims. They answer "what was it designed for," which the formal quality model treats as input rather than output.

---

## Signing

The manifest is a **predicate** — the statement of intent. Signing wraps it in a DSSE envelope or a sigstore bundle, the same way SBOM and SLSA attestations are signed today.

```
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{ "name": "metrics-dashboard-api", "digest": { "sha256": "..." } }],
  "predicateType": "https://software-architecture-spec.github.io/sam/v0.2",
  "predicate": { ...the manifest body... }
}
```

This means cosign, sigstore, and any in-toto-aware tooling can sign and verify SAMs without inventing a new key system. Bind the manifest to the artifact via `subject.digest`.

---

## Files

### v0.2 (current)

- `sam/v0.2/SPECIFICATION.md` — the normative specification (§§1–9)
- `sam/v0.2/schema.json` — the JSON Schema (Draft 2020-12)
- `sam/v0.2/examples/saas.manifest.json` — multi-tenant SaaS API (public-cloud shape)
- `sam/v0.2/examples/internal-enterprise.manifest.json` — internal employee-onboarding portal (corporate-internal shape: SSO, no public exposure, regulatory retention, WCAG 2.2 AA)
- `sam/v0.2/conformance/` — test corpus indexed by `manifest.json`; 8 positive cases, 12 negative cases, README with run instructions.

### Companion registries

- `registry/standards.json` — canonical spellings for `industryRefs.standard` (SPDX List pattern; advisory)
- `registry/tensions.json` — well-known IDs for `tensionsDeclared[].tension` (the five from §5.1.11)
- `registry/README.md` — registry shape, versioning, and contribution model

### v0.1 (frozen)

- `sam/v0.1/` — preserved at its URIs; new manifests should use v0.2.

### Validation

```sh
# Run all checks: schema metaschema, every version's examples, conformance corpus, registries.
python3 tools/validate.py
```

The validator (`tools/validate.py`) is the canonical entry point. It runs in:

- **CI on every push and pull request** to `main` via [`.github/workflows/validate.yml`](.github/workflows/validate.yml) — enforced for all proposed changes.
- **Locally as a pre-commit hook** if you opt in:

  ```sh
  git config core.hooksPath .githooks
  pip install jsonschema  # one-time
  ```

  After that, `git commit` runs the validator on any change touching `sam/`, `registry/`, the validator itself, or the CI workflow. Bypass with `git commit --no-verify` only when you understand what you're skipping.

For ad-hoc validation of a single example without the full corpus:

```sh
check-jsonschema --schemafile sam/v0.2/schema.json sam/v0.2/examples/saas.manifest.json
```

---

## Status

v0.2 — draft. Breaking changes still possible while `MAJOR` is `0` (per `SPECIFICATION.md §6.1`). The goal of v0 is to get the field set right, not to lock the format. v0.2 is additive over v0.1 (no breaking changes); v0.1 manifests remain conforming under their own URIs.

### v0.2 conventions

- **`x-*` extensions permitted** on `qualityAttributeClaim`, `qualityAttributes` characteristic objects, `tensionsDeclared[]` items, `industryRefs[]` items, `evidence[]` items, `producer`, and `subject.components[]` items. Forbidden on the top-level manifest, `subject` root, `manifestVersion`, `intent` (and `tenancy`), `qualityAttributes` parent, and all of `envelope`'s sub-blocks. See `SPECIFICATION.md §7`.
- **Stability annotations** on every field's `description` (`Stability: stable | experimental`) plus an `x-sam-stability` keyword on stable fields. See `SPECIFICATION.md §8`.
- **Open enums** for `tensionsDeclared.tension` and `industryRefs.standard` — `/registry/tensions.json` and `/registry/standards.json` provide advisory canonical IDs.
- **`informationalRefs[]` requires URIs.** Use https.

### Open questions

- Per-characteristic enum constraints on ISO 25010 sub-characteristic keys (currently any-string for ergonomics).
- Conditional `if/then` so `evidence` is required when `status: verified` and `summary` is required when `status: declared|verified` (currently §5.1.6/§5.1.7 enforced by spec only, surfaced in conformance corpus).
- Whether `tensionsDeclared` should be required (today: optional).
- Evidence verification: should the schema require evidence URIs to themselves be signed attestations?
- Whether to add a `lifecycle` section (active, maintenance, deprecated, abandoned) or leave that to package metadata.
- Subject-aware DSSE binding for non-artifact layers — service- and product-layer manifests have optional `subject.digest`; binding them to a subject identifier without a digest is currently underspecified.

### Planned beyond v0.2

- **Authoring guide** — practical guidance for producers on what to populate per attribute and how to write honest summaries.
- **Verification guide** — practical guidance for consumers on how to evaluate a SAM in different decision contexts.
- **Lifecycle policy** — re-issuance, revocation, supersession.
- **Tension and standards registry growth** — versioning, contribution workflow, alias curation.
- **`x-sam-stability` validation behavior** — currently descriptive; future versions may give it semantics (e.g., consumers reject manifests that promise `stable` and use `experimental` fields).

---

## License

This project is dual-licensed.

- **Code, schema, examples, conformance corpus, and registries** (`sam/**/schema.json`, `sam/**/examples/*`, `sam/**/conformance/*`, `registry/*.json`, future tooling) are licensed under [Apache-2.0](LICENSE). Apache-2.0 is preferred over MIT here because it includes an explicit patent grant — important for a standard with potential patent surface around signing and verification flows.
- **Specification text and other prose** (`README.md`, `sam/**/SPECIFICATION.md`, `registry/README.md`, `sam/**/conformance/README.md`) are licensed under [Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE-DOCS). This follows the convention used by SLSA and SPDX (newer versions) for normative spec text: derivative documents are permitted with attribution.

The intent of this repository is broad reuse with attribution.
