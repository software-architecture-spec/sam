# Software Architecture Manifest — Specification

Version: 0.1 (draft)
Status: Working draft. Breaking changes expected before v1.

This document is the normative reference for the Software Architecture Manifest (SAM). The accompanying [JSON Schema](schema.json) is the syntactic form; this document defines what conformance to that form means and what claims a SAM is asserting when it is signed.

This document is structured into eight sections:

1. **Scope** — what SAM is, what it isn't, who it's for
2. **Terminology** — the words this specification uses precisely
3. **Conformance language** — how to read MUST / SHOULD / MAY in the rest of the spec
4. **Threat model** — what SAM defends against, what it does not
5. **Definition of a conforming SAM** — the normative requirements for producers and consumers
6. **Versioning** — how this specification evolves and what guarantees consumers can rely on across versions
7. **Extensibility** — how producers extend a SAM without forking the schema
8. **Stability** — how individual fields signal their maturity to consumers

Authoring guides, verification guides, SAM levels (L0–L3), and lifecycle policy are deferred to a subsequent iteration of this specification.

---

## §1 Scope

### §1.1 What SAM is

A Software Architecture Manifest is a producer-signed, machine-readable declaration of:

1. **What the software was designed to do** — its purpose, intended audience, and tenancy model.
2. **The operational envelope it was designed for** — throughput, scaling axis, instantiation mode, privilege posture, network posture, and persistence requirements.
3. **The quality attributes the producer claims, with evidence where applicable** — performance, reliability, security, etc., per ISO/IEC 25010:2023, with cross-references to industry standards (NIST SSDF, OWASP ASVS, WCAG, OpenTelemetry, etc.).
4. **The tensions the producer has chosen postures on** — CAP/PACELC, observability cost trilemma, etc.

A SAM is a *predicate* in the in-toto sense. It is intended to be signed via DSSE / sigstore / cosign and bound to its subject by content digest. The signing mechanism is not specified here; this document defines only the predicate body.

A SAM may describe an artifact (a single signed deployable), a service (a logical SLO-owning unit composed of one or more artifacts), or a product (the contractual surface composed of one or more services). The granularity is declared explicitly via `subject.layer`.

### §1.2 What SAM is NOT

A SAM is not:

- A **build attestation**. SLSA covers how software was built. SAM covers what it was designed to do.
- A **bill of materials**. SBOM (CycloneDX, SPDX) covers what is inside the software. SAM covers what the software is for.
- A **vulnerability disclosure format**. That is CSAF / VEX.
- A **runtime telemetry format**. SAM declares design intent, not observed behavior.
- A **legal contract** or **service-level agreement**. A SAM carries no automatic legal weight; it asserts producer claims that a separate contract may incorporate by reference.
- A **license declaration**. That is SBOM territory.
- A **substitute for testing**. Evidence URIs reference verification artifacts; SAM is a pointer to verification, not verification itself.

### §1.3 Audience

SAM is designed to be read by three classes of consumer:

- **Producers** — OSS maintainers, software vendors, internal platform teams — who issue SAMs to declare what they built.
- **Consumers** — procurement, audit, security teams, SREs, downstream developers, and AI agents — who read SAMs to assess what they are adopting.
- **Tooling builders** — implementers of validators, signers, viewers, and CI integrations — who need a stable normative target.

### §1.4 Relationship to other specifications

SAM is intentionally scoped to coexist with, not replace, existing supply-chain artifacts:

| Layer | Existing standard | SAM relationship |
|---|---|---|
| Contents | SBOM (CycloneDX, SPDX) | Referenced via `subject.sbomRef` |
| Build provenance | SLSA, in-toto | SAM is a sibling predicate, signed via the same envelope |
| Quality model | ISO/IEC 25010:2023 | The spine of `qualityAttributes` |
| Vulnerabilities | CSAF, VEX | Out of scope; complementary |
| Software identity | OCI, package URLs | `subject.digest` and `subject.name` interoperate |

---

## §2 Terminology

The following terms are used with the meanings given here throughout this specification.

- **Artifact** — A single deployable unit: a container image, a binary, a package, or a library, identified by a content-addressed digest.
- **Service** — A logical unit composed of one or more artifacts that owns one or more service-level objectives.
- **Product** — A contractual or customer-facing offering composed of one or more services.
- **Subject** — The artifact, service, or product that a manifest describes. Declared in `subject` with a `layer` discriminator.
- **SAM** — A Software Architecture Manifest; an instance of the format defined by this specification.
- **Manifest** — A single SAM document.
- **Manifest version** — The schema version a manifest claims to conform to, declared in `manifestVersion`.
- **Predicate** — The manifest body when wrapped in an in-toto Statement for signing.
- **Predicate type URI** — The canonical URI identifying the SAM predicate format and version, set in the in-toto Statement's `predicateType` field. For this version: `https://software-architecture-spec.github.io/sam/v0.1`.
- **Producer** — The party that issues and signs a SAM. Declared in `producer.name`.
- **Consumer** — Any party that reads a SAM.
- **Claim** — A single statement of fact made in a SAM (e.g., a quality attribute claim, a tension posture).
- **Evidence** — A referenced artifact supporting a claim, identified by URI in `evidence[].uri`.
- **Quality attribute** — An ISO/IEC 25010:2023 characteristic (one of nine) or sub-characteristic.
- **Operational envelope** — The design-time target operating conditions declared in `envelope`.
- **Intent** — The purpose, audience, and tenancy model declared in `intent`.
- **Industry reference** — A normative pointer to an external standard, declared in `industryRefs[]`.
- **Informational reference** — A non-normative pointer to design-context resources, declared in `informationalRefs[]`.
- **Tension** — A coupled trade-off between quality attributes (e.g., consistency vs. availability vs. latency) on which the producer must choose a posture.
- **Conformance** — Adherence to this specification, as defined in §5.
- **Verification** — The process of checking that evidence supports a claim. Out of scope for this version.

---

## §3 Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

The same keywords appearing in lowercase in this document are not normative; they are used in their plain-English sense.

---

## §4 Threat model

SAM exists to address a specific class of failure mode in modern software supply: the visual signals that once distinguished a production-grade system from a weekend prototype have collapsed. Stack choice, deployment pipeline, and surface polish no longer correlate with design maturity. A consumer — human or AI — cannot tell from inspection which signals are load-bearing.

SAM is a producer-signed declaration that restores those signals explicitly. The threats it addresses, and the threats it does not, are enumerated below.

### §4.1 Threats SAM addresses

**T1 — Production-grade impersonation.** Software with weak design properties (no concurrency model, no failure-mode design, no security architecture) is mistaken for production-ready because its surface signals match those of mature systems.
*Mitigation:* a producer-signed manifest declares which quality attributes have been specified, declared, or verified, and which are honestly unspecified. The default (`status: unspecified`) is informative absence; consumers learn what was *not* designed for as well as what was.

**T2 — Operational envelope inference.** Consumers cannot tell, from a deployable, whether it was designed for one user or many; whether it scales horizontally; whether it expects internet access or runs isolated; whether it requires root or runs unprivileged.
*Mitigation:* `envelope` declares each of these as a structured field. Outside the envelope, behavior is undefined by the producer's own assertion.

**T3 — Tension hiding.** Distributed systems require choosing sides on CAP/PACELC, on observability cost vs. resolution, on test-suite coverage vs. maintainability. Producers often don't declare their posture, leaving consumers to discover the trade-off during an incident.
*Mitigation:* `tensionsDeclared` makes the posture and rationale explicit at design time.

**T4 — Citation drift.** Informal claims like "we're SOC 2 compliant" or "WCAG AA" travel in marketing copy without machine-readable substrate. Consumers cannot verify them programmatically.
*Mitigation:* `industryRefs[]` structures the citation (`standard`, `version`, `conformance`, `referenceUri`); `evidence[]` provides URIs to the verification artifacts.

**T5 — Composition opacity.** A product is many services; a service is many artifacts. A consumer reading a manifest at the wrong layer will misinterpret what they see (a service-layer claim of "horizontal scaling" does not imply each constituent artifact is independently scalable).
*Mitigation:* `subject.layer` declares granularity explicitly. `subject.components[]` makes composition explicit.

### §4.2 Threats SAM does NOT address

**N1 — Lying producers.** A SAM is what the producer says. A signed declaration of `verified` with fabricated evidence is detectable only by inspecting the evidence. SAM is no defense against a determined liar; its contribution is to make the lie *attributable* to a specific producer key in retrospect.

**N2 — Code-execution-time vulnerabilities.** A SAM is a design artifact, not a runtime guard. It tells consumers what to expect; it does not prevent attacks against running code.

**N3 — Stale claims.** A SAM issued 18 months ago may not reflect the current code. The `producer.validFor` field is advisory; consumers SHOULD check freshness against the artifact's current digest before relying on the manifest.

**N4 — Missing claims.** Honest absence (`status: unspecified`) is not a vulnerability. Over-claiming is. SAM cannot enforce honest claim-making; it can only make over-claiming auditable.

**N5 — Out-of-band channels.** A producer may make different claims in marketing materials, contract language, or sales decks than in the SAM. SAM cannot reconcile these; it provides one signed source of truth for the format and leaves reconciliation to the consumer's contract.

**N6 — License compliance.** Out of scope. Use SBOM (CycloneDX or SPDX) referenced via `subject.sbomRef`.

**N7 — Build provenance.** Out of scope. Use SLSA / in-toto attestations as siblings to the SAM.

**N8 — Vulnerability disclosure.** Out of scope. Use CSAF / VEX as siblings.

### §4.3 Trust assumptions

Consumers of a SAM rely on the following trust assumptions, none of which SAM itself enforces:

- The producer controls the signing key chain identified in the DSSE envelope.
- The signing key chain is resolvable to an organizational identity that the consumer can evaluate (e.g., via Sigstore Fulcio identities, GPG web of trust, or organizational PKI).
- `industryRefs[].standard` strings are interpretable in good faith. Ambiguous strings (e.g., bare `"27001"`) are non-conforming per §5.
- Evidence URIs may resolve to producer-controlled infrastructure; consumers SHOULD assess whether independent third-party attestation is required for high-stakes decisions.
- Two SAMs covering the same subject digest with different claims indicate either a producer error, a key compromise, or an out-of-band update; consumers MUST treat conflicting signed claims as an integrity failure to be resolved before adoption.

---

## §5 Definition of a conforming SAM

This section defines what it means for a SAM to conform to this specification. Conformance is defined in two tiers: **conforming** and **strictly conforming**. Tooling MUST follow the consumer rules below.

### §5.1 Conformance requirements (producers)

A SAM is **conforming** if all of the following hold:

1. The document is well-formed JSON per [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
2. The document validates against the JSON Schema published at the schema's `$id` for the declared `manifestVersion`.
3. The document is signed via DSSE per the [in-toto Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) format, with `predicateType` equal to the canonical predicate type URI for the declared `manifestVersion` (for v0.1: `https://software-architecture-spec.github.io/sam/v0.1`).
4. The DSSE signing key chain MUST be resolvable to an identity that asserts authority over the producer named in `producer.name`.
5. When `subject.layer` is `artifact`, `subject.digest` MUST be present and bind the manifest to the artifact via the in-toto Statement `subject` field.
6. When any `qualityAttributeClaim.status` is `verified`, at least one entry in `evidence[]` MUST be present for that claim.
7. When any `qualityAttributeClaim.status` is `declared` or `verified`, the `summary` field MUST be present and non-empty for that claim.
8. All URI fields (`evidence[].uri`, `informationalRefs[]`, `subject.sbomRef`, `subject.components[].manifestUri`, `industryRefs[].referenceUri`, `producer.contact` if a URI) MUST be syntactically valid URIs per [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986).
9. All `industryRefs[].standard` values MUST be interpretable as references to publicly identifiable standards. A bare numeric string (e.g., `"27001"`), an unqualified abbreviation (e.g., `"CSF"` without context), or a private vendor identifier is non-conforming.
10. `producer.issuedAt` MUST be a valid RFC 3339 / ISO 8601 timestamp not in the future relative to the producer's local clock at signing time.

A SAM is **strictly conforming** if, additionally:

11. All `tensionsDeclared[].tension` values are either well-known identifiers from the registry maintained alongside this specification (a future deliverable) or use the `x:` prefix for vendor-specific tensions.
12. No object contains property keys not defined in the schema. (This matches the schema's `additionalProperties: false`. v0.2 will introduce a vendor extension namespace via `x-*` keys; until then, strict conformance forbids unknown keys.)
13. `producer.validFor` is present, and the consumption time falls within `[producer.issuedAt, producer.issuedAt + producer.validFor]`.

### §5.2 Producer responsibilities

A producer:

- MUST NOT set `status: verified` for a claim without at least one corresponding `evidence` URI.
- MUST NOT set `status: verified` for a claim that has not actually been verified by the producer or a party the producer relies on. This is a moral, not technical, requirement; the signature attributes any violation to the producer's key.
- SHOULD use `status: unspecified` honestly when no claim is being made. Honest absence is preferable to fabricated assurance.
- SHOULD use `status: not_applicable` only when the attribute is genuinely irrelevant to the artifact (e.g., `interactionCapability` for a backend API with no UI surface).
- SHOULD avoid overstating conformance levels in `industryRefs[].conformance`. A self-attestation to NIST SSDF practices is not equivalent to a third-party SOC 2 Type 2 audit; the `conformance` string SHOULD make this distinction visible.
- SHOULD re-issue the SAM when the underlying artifact's content digest changes. A SAM whose claims no longer match the artifact's current state is a correctness hazard.

### §5.3 Consumer responsibilities

A consumer of a SAM:

- MUST reject documents that fail items §5.1.1 (well-formed JSON), §5.1.2 (schema validation), §5.1.3 (DSSE envelope), §5.1.4 (signing identity), §5.1.5 (digest binding), §5.1.6 (evidence-when-verified), §5.1.7 (summary-when-declared-or-verified), or §5.1.10 (timestamp validity).
- SHOULD reject documents that fail items §5.1.8 (URI validity) or §5.1.9 (interpretable standard strings) unless operating in a trusted context where the producer is independently known.
- SHOULD warn when a SAM is conforming but not strictly conforming.
- MUST treat two SAMs with the same `subject.digest` and conflicting claims as an integrity failure requiring resolution before adoption.
- SHOULD consult `producer.validFor` to assess freshness. A SAM beyond its validity window MAY still be informative but SHOULD be treated as advisory only.
- MAY accept non-conforming documents in trusted contexts (e.g., internal-use software from a known team) but MUST flag the non-conformance to downstream consumers.

### §5.4 Tooling responsibilities

A validator:

- MUST report which conformance items in §5.1 a document fails.
- MUST distinguish between "fails conformance" and "fails strict conformance."
- SHOULD report producer-responsibility violations (§5.2) when detectable from the document alone (e.g., a claim with `status: verified` and no `evidence`), but the validator's authority extends only to what is visible in the document; it cannot adjudicate whether evidence URIs themselves substantiate the claims they support.

A signer:

- MUST produce a DSSE envelope per §5.1.3.
- MUST set `predicateType` to the canonical URI for the manifest version being signed.
- SHOULD record the signing identity in a manner that allows downstream consumers to resolve §5.1.4.

A viewer:

- SHOULD render `unspecified` claims with the same visual weight as `declared` and `verified` claims, so that consumers see honest absence rather than scrolling past it.
- SHOULD distinguish `declared` (no evidence) from `verified` (evidence present) in the visual surface.

---

## §6 Versioning

This specification, the JSON Schema, and the predicate type URI are versioned together. Consumers MUST be able to rely on stable compatibility guarantees across versions; producers MUST be able to upgrade with predictable cost.

### §6.1 Version identifiers

SAM uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (`MAJOR.MINOR.PATCH`).

- The current version is **0.1**.
- While `MAJOR` is `0`, this specification is a working draft. Breaking changes MAY occur in minor releases.
- The first `MAJOR` ≥ 1 release is the first stable version. From that point on, the compatibility commitments in §6.3 apply strictly.

The version a manifest claims to conform to is declared in the top-level `manifestVersion` field. The same version appears in:

- The JSON Schema's `$id` path component (e.g., `.../v0.1.json`).
- The in-toto predicate type URI (e.g., `https://software-architecture-spec.github.io/sam/v0.1`).

These three values MUST agree for a given manifest.

### §6.2 What each version-bump tier means

A change is **PATCH** when it is editorial and does not change the schema, the predicate type URI, or any normative requirement. Examples: typo fixes, prose clarifications, non-normative example updates. Tools MUST treat the patched and unpatched versions as interchangeable. Tools that pin to a `MAJOR.MINOR.PATCH` triple MUST also accept any later `PATCH` of the same `MAJOR.MINOR`.

A change is **MINOR** when it is additive: new optional fields, new optional sub-objects, new well-known enum values added to open enums. A manifest that conformed to `MAJOR.MINOR_OLD` MUST conform to any later `MAJOR.MINOR_NEW` of the same `MAJOR`. New consumers MUST be able to read manifests issued against earlier minor versions of the same major version.

A change is **MAJOR** when it is breaking: removing a field, narrowing a value space, changing the meaning of an existing field, changing required-vs-optional status, or changing the predicate type URI. A manifest issued at one `MAJOR` MAY be invalid under the schema of the next `MAJOR`. The predicate type URI changes (e.g., `sam/v1` → `sam/v2`).

### §6.3 Compatibility commitments

For any two versions `A` and `B` of this specification where `A < B`:

- **Same MAJOR:** A consumer of version `B` MUST accept manifests claiming any earlier minor or patch version of the same major. A producer using version `A` MUST be able to upgrade to `B` without re-issuing existing manifests, except by their own choice.
- **Different MAJOR:** A consumer of version `B` MUST NOT silently treat a manifest claiming version `A` as a `B` manifest. The consumer SHOULD either reject the manifest, accept it in compatibility mode (validating against the `A` schema), or surface the version mismatch to the operator.

### §6.4 Predicate type URI policy

The canonical predicate type URI for this specification is of the form:

    https://software-architecture-spec.github.io/sam/v<MAJOR>[.<MINOR>]

For pre-1.0 working drafts, the URI includes the minor version (`v0.1`, `v0.2`). For stable versions (`MAJOR ≥ 1`), the URI includes only the major version (`v1`, `v2`); minor versions of a stable major share a single URI because they are backward compatible by §6.3.

A signing tool MUST NOT set `predicateType` to a URI different from the one declared in `manifestVersion`. A verifier MUST treat such a mismatch as an integrity failure.

### §6.5 Deprecation

A field, value, or sub-object MAY be marked **deprecated** in a minor version. Deprecation does not remove the field; it signals intent to remove it in the next major version. Deprecated fields:

- MUST continue to validate against the schema until the next major version.
- MUST list a successor field, value, or pattern in their description, or MUST state "removed without replacement" with rationale.
- MUST NOT be reintroduced under the same name with different semantics in a future version.

Producers SHOULD migrate away from deprecated fields. Consumers MUST continue to accept deprecated fields in any minor version of the major in which they were deprecated.

---

## §7 Extensibility

SAM is intentionally narrow. Producers will need fields this specification does not provide. To allow growth without forking the schema, SAM follows the convention used by OpenAPI, CycloneDX, and Kubernetes: a vendor extension namespace.

### §7.1 The `x-*` extension namespace

Custom keys MUST be prefixed with `x-` (lowercase `x` followed by a hyphen). Custom keys SHOULD include a stable namespace identifier after the prefix to avoid collisions:

    x-<namespace>-<key>

Examples: `x-acme-deploy-region`, `x-redhat-fips-mode`, `x-internal-cost-center`.

The namespace `x-sam-` is **reserved** for future additions defined by working-group consensus on this specification. Producers MUST NOT use `x-sam-` for vendor-specific extensions.

### §7.2 Where extensions are permitted

Custom `x-*` keys MAY appear on the following objects:

- Each `qualityAttributeClaim` (the inner object containing `status`, `summary`, `evidence`, `industryRefs`, `informationalRefs`).
- Each ISO 25010 characteristic object inside `qualityAttributes` (the object containing `overall` and `subCharacteristics`).
- Each entry in the `extensions` block.
- Each entry in `tensionsDeclared[]`.
- Each entry in `industryRefs[]` and each entry in `evidence[]`.
- The `producer` object.
- Each entry in `subject.components[]`.

Custom `x-*` keys MUST NOT appear on the following objects, where unknown fields would change conformance-relevant semantics:

- The top-level manifest object.
- `subject` (signing-relevant; changes here would invalidate the digest binding).
- `manifestVersion`.
- `intent`, `envelope`, and any of `envelope`'s sub-blocks (`throughput`, `scaling`, `instantiation`, `privilege`, `network`, `persistence`). Producers needing additional operational claims SHOULD use the `extensions` block instead.

A future minor version of the JSON Schema will add `patternProperties: { "^x-": {} }` to the permitted objects. Until then, strict conformance (§5.1.12) forbids unknown keys; extensions are permitted only on objects whose schema declarations include `additionalProperties: true` or a matching `patternProperties` entry.

### §7.3 What extensions may not do

An extension MUST NOT:

- Contradict any normative claim made elsewhere in the manifest. (E.g., `x-acme-multi-tenant: true` on a manifest with `intent.audience: single_user` is non-conforming.)
- Be required for a consumer to evaluate the manifest's normative content.
- Be relied on by a verifier as a basis for conformance decisions.

An extension MAY:

- Carry vendor-specific operational metadata (deployment regions, cost-center attribution, internal ticket IDs).
- Carry experimental fields the producer expects to propose for inclusion in a future minor version.
- Reference internal evidence stores, internal namespaces, or internal taxonomies.

### §7.4 Tooling expectations

- A validator MUST accept any `x-*` key on a permitted object without error.
- A re-emitting tool (e.g., one that reads a manifest, modifies it, and writes it back) SHOULD preserve unknown `x-*` keys it does not recognize, to avoid silent loss of producer intent.
- A viewer SHOULD render unknown `x-*` keys distinctly from normative fields, so consumers do not mistake them for spec-defined claims.

---

## §8 Stability

Not every field in the schema carries the same maturity. Some are well-grounded in established standards (the `qualityAttributes` keys come from ISO/IEC 25010:2023). Some are intentionally exploratory (the `contextWindowManagement` extension addresses an AI-era concern with no formal home in any quality model yet). Consumers need to know which is which to plan their reliance.

### §8.1 Stability tiers

Every field defined by this specification is in exactly one of three tiers:

- **stable** — The field, its name, and its semantics will not change except in a `MAJOR` version bump. Tools MAY rely on it indefinitely within a major version.
- **experimental** — The field exists, but its name, structure, value space, or semantics MAY change in any `MINOR` version. Tools MAY use it but SHOULD be prepared for change.
- **deprecated** — The field is scheduled for removal in the next `MAJOR` version. Tools MUST continue to accept it until that version. Producers SHOULD migrate. The deprecation notice MUST cite a successor or state "removed without replacement."

### §8.2 Default tier in v0

For this draft, **all fields defined by this specification are `experimental`** unless explicitly marked otherwise. The first `MAJOR ≥ 1` release will mark the foundational set as `stable`. Consumers using v0 SHOULD plan for minor-version churn.

### §8.3 How fields declare their stability

In the JSON Schema, a field's stability tier is declared in its `description` text using the convention:

    Stability: stable | experimental | deprecated [— <notes>]

Where `<notes>` MAY include a successor reference (`see x.y.z`), a deprecation rationale, or expected-change scope. Fields without an explicit annotation default to the version's default tier (`experimental` while `MAJOR` is `0`; `stable` after).

A future minor version of the JSON Schema will surface stability via a structured custom keyword (e.g., `x-sam-stability`) so that tooling can read it without parsing prose. The `description`-prefix convention is the v0 placeholder.

### §8.4 Promotion and demotion

A field MAY be promoted from `experimental` to `stable` in any minor version. Promotion is non-breaking by definition.

A field MAY be demoted from `stable` to `deprecated` in any minor version. Demotion is non-breaking; the field continues to validate. Removal of a deprecated field requires a major version bump (§6.5).

A field MUST NOT move from `experimental` to `deprecated` without an intervening promotion to `stable` or a major version bump. (Rationale: producers should not be punished for using a field the spec said was experimental; the path to removal goes through stable.)

---

## Open issues

The following are deliberately deferred from this version of the specification:

- **SAM levels** (L0–L3) — a tiered conformance model analogous to SLSA build levels.
- **Authoring guide** — practical guidance for producers on what to populate per attribute and how to write honest summaries.
- **Verification guide** — practical guidance for consumers on how to evaluate a SAM in different decision contexts.
- **Lifecycle policy** — re-issuance, revocation, supersession.
- **Schema implementation of §7** — adding `patternProperties: { "^x-": {} }` to the objects listed in §7.2.
- **Schema implementation of §8** — annotating each field's `description` with its stability tier, and introducing an `x-sam-stability` keyword.
- **Canonical-strings registry** — managed list of approved spellings for `industryRefs.standard` values.
- **Tension identifier registry** — the registry referenced in §5.1.11.
- **Conformance test suite** — corpus of known-good and known-bad manifests with expected validator outputs, including positive and negative cases for each conformance item in §5.1.

These will be addressed in subsequent iterations of this specification once §§1–8 stabilize.
