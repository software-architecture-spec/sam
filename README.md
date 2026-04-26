# Design Intent Manifest (DIM)

A producer-signed, machine-readable declaration of what a software artifact was designed to do and the operational envelope it was designed for.

SBOM tells you what's inside the artifact. SLSA tells you how it was built. OpenSSF Scorecard tells you whether good practices were followed. **DIM tells you what the producer designed it to be.**

> A nutrition label for architecture, signed by the maintainer, shipped on every artifact.

This is the v0 schema. Companion to *Designed to Fail* (essay) and the [Banyan NFR trunk](https://banyan.vamitra.com/trunk/bnyn-10b6f56d).

---

## Why

In the AI era, a vibe-coded weekend prototype and a hardened production service are visually indistinguishable: same React frontend, same Postgres, same Dockerfile, same deployment pipeline. The Access database on a shared drive used to advertise its own fragility. The modern equivalent does not.

DIM restores that signal. A manifest that honestly declares `audience: single_user`, `scaling: none`, `observability: unspecified`, `tenancy: none` *is* the modern `.mdb` file announcing what it is — without the ambiguity of inference from stack choices.

---

## Layers — what a manifest describes

The same questions ("how does it scale", "what privilege does it run with", "is it multi-tenant") get different answers at three different layers, read by three different audiences. A DIM declares its layer explicitly via `subject.layer`:

| Layer | Granularity | Audience | Notes |
|---|---|---|---|
| `artifact` | one container image, binary, or package | AI agents, build/SLSA, SBOM tooling | The signing granularity. `digest` is required. Matches in-toto subject convention. |
| `service` | a logical SLO-owning unit (1+ artifacts) | SRE, on-call, ops | Where SLOs and incident response actually live. `digest` optional; uses `components[]` to point at constituent artifact DIMs. |
| `product` | the contractual / customer-facing surface | Procurement, audit, customers | What gets sold. `components[]` points at constituent service DIMs. |

A small project may only need one DIM at the `artifact` layer. A real product typically has all three, with each layer's manifest referencing its constituents via `subject.components[]`. Composition is explicit; nothing is inferred.

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
│   ├── internationalization
│   └── contextWindowManagement   AI-era concern
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

DIM uses two reference layers per claim:

- **`industryRefs[]`** — *normative*. Industry-standard anchors that auditors and procurement teams recognize. First-class on the manifest because they outlive any single host or vendor.
- **`informationalRefs[]`** — *non-normative*. Pointers to design context (pattern catalogs, internal docs, the Banyan trunk) that aided the producer's reasoning. Useful for AI agents and humans who want to drill into rationale; not anchors an auditor relies on.

### Top-level standards

| Layer | Standard | Where it lives |
|---|---|---|
| Software supply chain (contents) | SBOM (CycloneDX / SPDX) | `subject.sbomRef` |
| Build provenance | SLSA / in-toto | external attestation; DIM is a sibling predicate |
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

### Why the Banyan trunk is informational, not normative

The Banyan trunk `bnyn-10b6f56d` is the best content source for AI-prompt-ready NFR guidance — the trunk's `what:requirement / how:pattern / when:trigger` shape is action-oriented in a way ISO 25010's prose is not. But Banyan is single-vendor, single-host, and the IDs (`bnyn-9559c09c`) mean nothing in a compliance review. References on a *signed* artifact need to outlive any host they point at.

So Banyan references live in `informationalRefs[]` (using a `banyan://<id>` URI shape), and the normative weight sits with `industryRefs[]`. AI agents reading the manifest can dereference the Banyan link for prompt context; auditors ignore it and read the industry anchors.

### Why ISO 25010, but not only

ISO 25010:2023 was adopted as the canonical key set for `qualityAttributes` because it is the formal quality model that procurement, audits, and certifications already speak. Producers can populate the `overall` claim per characteristic for a coarse manifest, or drill into `subCharacteristics` for a granular one.

ISO 25010 has known gaps for AI-era systems. Observability has no first-class home (it folds under `maintainability.analysability`); data lifecycle, i18n, and AI-context-window concerns have no formal home at all. These live in `extensions`.

The operational `envelope` (tenancy, instantiation mode, privilege, network posture) is intentionally not part of `qualityAttributes` — these are deployment/operational signals, not quality claims. They answer "what was it designed for," which the formal quality model treats as input rather than output.

---

## Signing

The manifest is a **predicate** — the statement of intent. Signing wraps it in a DSSE envelope or a sigstore bundle, the same way SBOM and SLSA attestations are signed today.

```
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{ "name": "metrics-dashboard-api", "digest": { "sha256": "..." } }],
  "predicateType": "https://quality-software.dev/dim/v0.1",
  "predicate": { ...the manifest body... }
}
```

This means cosign, sigstore, and any in-toto-aware tooling can sign and verify DIMs without inventing a new key system. Bind the manifest to the artifact via `subject.digest`.

---

## Files

- `schema/design-intent-manifest.v0.schema.json` — the JSON Schema (Draft 2020-12)
- `examples/example.manifest.json` — multi-tenant SaaS API (the public-cloud shape)
- `examples/internal-enterprise.manifest.json` — internal employee-onboarding portal (the corporate-internal shape: SSO, no public exposure, regulatory retention, WCAG 2.2 AA)

Validate with any JSON Schema validator (e.g., `ajv`, `check-jsonschema`):

```sh
check-jsonschema --schemafile schema/design-intent-manifest.v0.schema.json examples/example.manifest.json
check-jsonschema --schemafile schema/design-intent-manifest.v0.schema.json examples/internal-enterprise.manifest.json
```

---

## Status

v0.1 — draft, breaking changes expected. The goal of v0 is to get the field set right, not to lock the format. Open questions:

- Per-characteristic enum constraints on ISO 25010 sub-characteristic keys (currently any-string for ergonomics).
- Whether `tensionsDeclared` should be required or optional.
- Evidence verification: should the schema demand the evidence URI is itself a signed attestation?
- Whether to add a `lifecycle` section (active, maintenance, deprecated, abandoned) or leave that to package metadata.
