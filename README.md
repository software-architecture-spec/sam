# Software Architecture Manifest (SAM)

A producer-signed, machine-readable declaration of what software was designed to do and the operational envelope it was designed for.

SBOM tells you what's inside the software. SLSA tells you how it was built. OpenSSF Scorecard tells you whether good practices were followed. **SAM tells you what the producer designed it to be.**

> A nutrition label for architecture, signed by the maintainer, shipped on every artifact.

This is the v0 schema.

> **Normative reference.** The [SPECIFICATION.md](sam/v0.1/SPECIFICATION.md) document is the normative source for what a conforming SAM is and means. The JSON Schema in this repo is the syntactic form; the specification defines what conformance to that form requires. §§1–8 of the specification (Scope, Terminology, Conformance language, Threat model, Definition of a conforming SAM, Versioning, Extensibility, Stability) are written. SAM levels (L0–L3), authoring guide, verification guide, and lifecycle policy are deferred.

> **Note on the namespace.** The schema's `$id` (`https://software-architecture-spec.github.io/sam/v0.1/schema.json`) is hosted on GitHub Pages under the `software-architecture-spec` org. For SAM to become a useful cross-vendor standard, the namespace should eventually live with a neutral host (e.g., a CNCF / OpenSSF / IETF working group). The current host is appropriate for a working draft; URIs will redirect when the namespace moves.

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

## Structure

```
manifest
├── manifestVersion          schema version (v0.1)
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
│   └── persistence          required stores
├── qualityAttributes        ISO/IEC 25010:2023 — 9 characteristics + sub-characteristics
├── extensions               quality concerns ISO 25010 doesn't cover cleanly
│   ├── observability        (folds awkwardly under maintainability.analysability)
│   ├── dataLifecycle        retention, deletion, archival
│   └── internationalization
├── tensionsDeclared         which side of CAP/observability-cost/etc. did you pick?
└── producer                 issuer + contact + issuedAt + validFor
```

### Claim status

Every quality attribute claim has one of four statuses:

- `unspecified` — the producer makes no claim. (Honest absence is better than fake assurance.)
- `declared` — the producer asserts but provides no evidence. (Take their word for it.)
- `verified` — the producer asserts and points to evidence (load test, security scan, audit, CI run).
- `not_applicable` — the producer claims this attribute is irrelevant for this artifact.

This three-track model (declared / verified / unspecified) mirrors how SBOM standards grew attestation lanes over time. v0 is friendly to declared-only manifests; v1 will define stricter attestation requirements for the `verified` track.

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

### Per-section industry anchors (use as `industryRefs[]`)

| Section | Recommended anchors |
|---|---|
| `qualityAttributes.security.*` | NIST SP 800-218 (SSDF), OWASP ASVS L1/L2/L3, ISO/IEC 27001, SOC 2, NIST SP 800-53 |
| `qualityAttributes.interactionCapability.inclusivity` | WCAG 2.2 (A / AA / AAA), EN 301 549, Section 508 |
| `qualityAttributes.compatibility.interoperability` | OpenAPI 3.x, AsyncAPI, SCIM, SAML, OAuth 2.x, OIDC |
| `qualityAttributes.flexibility.installability` | OCI Image Spec, Helm chart schema |
| `qualityAttributes.safety` (domain-specific) | ISO 26262 (automotive), IEC 62304 (medical), DO-178C (aviation), IEC 61508 (industrial) |
| `qualityAttributes.functionalSuitability` | ISO/IEC 25010:2023 (correctness/completeness/appropriateness) |
| `extensions.observability` | OpenTelemetry semantic conventions |
| `extensions.dataLifecycle` | ISO/IEC 25012, GDPR articles, CCPA, HIPAA, SOX §802, PCI DSS |
| `extensions.internationalization` | Unicode CLDR, ICU MessageFormat, BCP 47 |
| Build / supply chain (top-level) | SLSA build level (L0–L3, where L0 = no claim), in-toto attestation, CycloneDX/SPDX |

These are starting points, not an exhaustive list. Producers populate `industryRefs[]` with whatever standards their audit/procurement context actually recognizes. The schema does not constrain the `standard` field to an enum — interoperability with industry catalogs takes precedence over schema-side validation.

### Why ISO 25010, but not only

ISO 25010:2023 was adopted as the canonical key set for `qualityAttributes` because it is the formal quality model that procurement, audits, and certifications already speak. Producers can populate the `overall` claim per characteristic for a coarse manifest, or drill into `subCharacteristics` for a granular one.

ISO 25010 has gaps. Observability has no first-class home (it folds under `maintainability.analysability`); data lifecycle and i18n have no formal home at all. These live in `extensions`.

The operational `envelope` (tenancy, instantiation mode, privilege, network posture) is intentionally not part of `qualityAttributes` — these are deployment/operational signals, not quality claims. They answer "what was it designed for," which the formal quality model treats as input rather than output.

---

## Signing

The manifest is a **predicate** — the statement of intent. Signing wraps it in a DSSE envelope or a sigstore bundle, the same way SBOM and SLSA attestations are signed today.

```
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{ "name": "metrics-dashboard-api", "digest": { "sha256": "..." } }],
  "predicateType": "https://software-architecture-spec.github.io/sam/v0.1",
  "predicate": { ...the manifest body... }
}
```

This means cosign, sigstore, and any in-toto-aware tooling can sign and verify SAMs without inventing a new key system. Bind the manifest to the artifact via `subject.digest`.

---

## Files

- `sam/v0.1/SPECIFICATION.md` — the normative specification
- `sam/v0.1/schema.json` — the JSON Schema (Draft 2020-12)
- `sam/v0.1/examples/saas.manifest.json` — multi-tenant SaaS API (public-cloud shape)
- `sam/v0.1/examples/internal-enterprise.manifest.json` — internal employee-onboarding portal (corporate-internal shape: SSO, no public exposure, regulatory retention, WCAG 2.2 AA)

Validate with any JSON Schema validator (e.g., `ajv`, `check-jsonschema`):

```sh
check-jsonschema --schemafile sam/v0.1/schema.json sam/v0.1/examples/saas.manifest.json
check-jsonschema --schemafile sam/v0.1/schema.json sam/v0.1/examples/internal-enterprise.manifest.json
```

---

## Status

v0.1 — draft. Breaking changes expected. The goal of v0 is to get the field set right, not to lock the format.

### v0 conventions

- **Strict objects.** All schema objects use `additionalProperties: false`. Vendor extensions are deferred to v0.2 (see below).
- **Open enums where the taxonomy is still forming.** `tensionsDeclared.tension` is an open string with documented well-known IDs (`cap_pacelc`, `observability_cost_trilemma`, etc.). For domain-specific tensions, use a stable identifier of your own with the prefix `x:` (e.g., `x:tenant_isolation_vs_cost`). Same convention will be used for any future open vocabularies.
- **Free-text `industryRefs.standard`.** Citation strings will drift ("ISO 27001" vs "ISO/IEC 27001"). A canonical-strings registry (SPDX License List pattern) is planned as a companion artifact, not as schema-side enum enforcement.
- **`informationalRefs[]` requires URIs.** Use https. No private URI schemes.

### Open questions

- Per-characteristic enum constraints on ISO 25010 sub-characteristic keys (currently any-string for ergonomics).
- Conditional `if/then` so `evidence` is required when `status: verified` and `summary` is required when `status: declared|verified`.
- Whether `tensionsDeclared` should be required (today: optional).
- Evidence verification: should the schema require evidence URIs to themselves be signed attestations?
- Whether to add a `lifecycle` section (active, maintenance, deprecated, abandoned) or leave that to package metadata.

### Planned for v0.2 / next sessions

- **Narrative continuation** — SAM levels (L0 = no manifest, L1 = declared-only, L2 = with `industryRefs`, L3 = verified with evidence), authoring guide, verification guide, lifecycle policy. (§§1–8 written in [SPECIFICATION.md](sam/v0.1/SPECIFICATION.md): scope, terminology, conformance language, threat model, conforming-SAM definition, versioning, extensibility, stability.)
- **Schema implementation of §7 (extensibility).** Add `patternProperties: { "^x-": {} }` to the objects §7.2 permits (`qualityAttributeClaim`, `qualityAttributes` characteristic objects, `extensions` entries, `tensionsDeclared[]`, `industryRefs[]`, `evidence[]`, `producer`, `subject.components[]`). Policy is normative now; schema implementation lands in v0.2.
- **Schema implementation of §8 (stability).** Annotate each field's `description` with its stability tier; introduce an `x-sam-stability` structured keyword for tooling.
- **Canonical-strings registry** for `industryRefs.standard` to reduce citation drift (SPDX License List pattern).
- **Tension identifier registry** for `tensionsDeclared[].tension` well-known IDs (referenced by §5.1.11).
- **Conformance test suite** — a corpus of known-good and known-bad manifests with expected validator outputs, with positive and negative cases for each conformance item in §5.1.
- **Anchor-gap closures** flagged by the citations audit: `envelope.privilege` + `envelope.network` → CIS Benchmarks / NIST SP 800-190; `extensions.dataLifecycle` deletion side → NIST SP 800-88 Rev. 1.

---

## License

This project is dual-licensed.

- **Code, schema, and examples** (`sam/v0.1/schema.json`, `sam/v0.1/examples/*`, future tooling) are licensed under [Apache-2.0](LICENSE). Apache-2.0 is preferred over MIT here because it includes an explicit patent grant — important for a standard with potential patent surface around signing and verification flows.
- **Specification text and other prose** (`README.md`, `sam/v0.1/SPECIFICATION.md`) are licensed under [Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE-DOCS). This follows the convention used by SLSA and SPDX (newer versions) for normative spec text: derivative documents are permitted with attribution.

The intent of this repository is broad reuse with attribution.
