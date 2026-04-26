# Design Intent Manifest — Specification

Version: 0.1 (draft)
Status: Working draft. Breaking changes expected before v1.

This document is the normative reference for the Design Intent Manifest (DIM). The accompanying [JSON Schema](schema/design-intent-manifest.v0.schema.json) is the syntactic form; this document defines what conformance to that form means and what claims a DIM is asserting when it is signed.

This document is structured into five sections:

1. **Scope** — what DIM is, what it isn't, who it's for
2. **Terminology** — the words this specification uses precisely
3. **Conformance language** — how to read MUST / SHOULD / MAY in the rest of the spec
4. **Threat model** — what DIM defends against, what it does not
5. **Definition of a conforming DIM** — the normative requirements for producers and consumers

Authoring guides, verification guides, DIM levels (L0–L3), and lifecycle policy are deferred to a subsequent iteration of this specification.

---

## §1 Scope

### §1.1 What DIM is

A Design Intent Manifest is a producer-signed, machine-readable declaration of:

1. **What the software was designed to do** — its purpose, intended audience, and tenancy model.
2. **The operational envelope it was designed for** — throughput, scaling axis, instantiation mode, privilege posture, network posture, and persistence requirements.
3. **The quality attributes the producer claims, with evidence where applicable** — performance, reliability, security, etc., per ISO/IEC 25010:2023, with cross-references to industry standards (NIST SSDF, OWASP ASVS, WCAG, OpenTelemetry, etc.).
4. **The tensions the producer has chosen postures on** — CAP/PACELC, observability cost trilemma, etc.

A DIM is a *predicate* in the in-toto sense. It is intended to be signed via DSSE / sigstore / cosign and bound to its subject by content digest. The signing mechanism is not specified here; this document defines only the predicate body.

A DIM may describe an artifact (a single signed deployable), a service (a logical SLO-owning unit composed of one or more artifacts), or a product (the contractual surface composed of one or more services). The granularity is declared explicitly via `subject.layer`.

### §1.2 What DIM is NOT

A DIM is not:

- A **build attestation**. SLSA covers how software was built. DIM covers what it was designed to do.
- A **bill of materials**. SBOM (CycloneDX, SPDX) covers what is inside the software. DIM covers what the software is for.
- A **vulnerability disclosure format**. That is CSAF / VEX.
- A **runtime telemetry format**. DIM declares design intent, not observed behavior.
- A **legal contract** or **service-level agreement**. A DIM carries no automatic legal weight; it asserts producer claims that a separate contract may incorporate by reference.
- A **license declaration**. That is SBOM territory.
- A **substitute for testing**. Evidence URIs reference verification artifacts; DIM is a pointer to verification, not verification itself.

### §1.3 Audience

DIM is designed to be read by three classes of consumer:

- **Producers** — OSS maintainers, software vendors, internal platform teams — who issue DIMs to declare what they built.
- **Consumers** — procurement, audit, security teams, SREs, downstream developers, and AI agents — who read DIMs to assess what they are adopting.
- **Tooling builders** — implementers of validators, signers, viewers, and CI integrations — who need a stable normative target.

### §1.4 Relationship to other specifications

DIM is intentionally scoped to coexist with, not replace, existing supply-chain artifacts:

| Layer | Existing standard | DIM relationship |
|---|---|---|
| Contents | SBOM (CycloneDX, SPDX) | Referenced via `subject.sbomRef` |
| Build provenance | SLSA, in-toto | DIM is a sibling predicate, signed via the same envelope |
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
- **DIM** — A Design Intent Manifest; an instance of the format defined by this specification.
- **Manifest** — A single DIM document.
- **Manifest version** — The schema version a manifest claims to conform to, declared in `manifestVersion`.
- **Predicate** — The manifest body when wrapped in an in-toto Statement for signing.
- **Predicate type URI** — The canonical URI identifying the DIM predicate format and version, set in the in-toto Statement's `predicateType` field. For this version: `https://quality-software.dev/dim/v0.1`.
- **Producer** — The party that issues and signs a DIM. Declared in `producer.name`.
- **Consumer** — Any party that reads a DIM.
- **Claim** — A single statement of fact made in a DIM (e.g., a quality attribute claim, a tension posture).
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

DIM exists to address a specific class of failure mode in modern software supply: the visual signals that once distinguished a production-grade system from a weekend prototype have collapsed. Stack choice, deployment pipeline, and surface polish no longer correlate with design maturity. A consumer — human or AI — cannot tell from inspection which signals are load-bearing.

DIM is a producer-signed declaration that restores those signals explicitly. The threats it addresses, and the threats it does not, are enumerated below.

### §4.1 Threats DIM addresses

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

### §4.2 Threats DIM does NOT address

**N1 — Lying producers.** A DIM is what the producer says. A signed declaration of `verified` with fabricated evidence is detectable only by inspecting the evidence. DIM is no defense against a determined liar; its contribution is to make the lie *attributable* to a specific producer key in retrospect.

**N2 — Code-execution-time vulnerabilities.** A DIM is a design artifact, not a runtime guard. It tells consumers what to expect; it does not prevent attacks against running code.

**N3 — Stale claims.** A DIM issued 18 months ago may not reflect the current code. The `producer.validFor` field is advisory; consumers SHOULD check freshness against the artifact's current digest before relying on the manifest.

**N4 — Missing claims.** Honest absence (`status: unspecified`) is not a vulnerability. Over-claiming is. DIM cannot enforce honest claim-making; it can only make over-claiming auditable.

**N5 — Out-of-band channels.** A producer may make different claims in marketing materials, contract language, or sales decks than in the DIM. DIM cannot reconcile these; it provides one signed source of truth for the format and leaves reconciliation to the consumer's contract.

**N6 — License compliance.** Out of scope. Use SBOM (CycloneDX or SPDX) referenced via `subject.sbomRef`.

**N7 — Build provenance.** Out of scope. Use SLSA / in-toto attestations as siblings to the DIM.

**N8 — Vulnerability disclosure.** Out of scope. Use CSAF / VEX as siblings.

### §4.3 Trust assumptions

Consumers of a DIM rely on the following trust assumptions, none of which DIM itself enforces:

- The producer controls the signing key chain identified in the DSSE envelope.
- The signing key chain is resolvable to an organizational identity that the consumer can evaluate (e.g., via Sigstore Fulcio identities, GPG web of trust, or organizational PKI).
- `industryRefs[].standard` strings are interpretable in good faith. Ambiguous strings (e.g., bare `"27001"`) are non-conforming per §5.
- Evidence URIs may resolve to producer-controlled infrastructure; consumers SHOULD assess whether independent third-party attestation is required for high-stakes decisions.
- Two DIMs covering the same subject digest with different claims indicate either a producer error, a key compromise, or an out-of-band update; consumers MUST treat conflicting signed claims as an integrity failure to be resolved before adoption.

---

## §5 Definition of a conforming DIM

This section defines what it means for a DIM to conform to this specification. Conformance is defined in two tiers: **conforming** and **strictly conforming**. Tooling MUST follow the consumer rules below.

### §5.1 Conformance requirements (producers)

A DIM is **conforming** if all of the following hold:

1. The document is well-formed JSON per [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
2. The document validates against the JSON Schema published at the schema's `$id` for the declared `manifestVersion`.
3. The document is signed via DSSE per the [in-toto Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) format, with `predicateType` equal to the canonical predicate type URI for the declared `manifestVersion` (for v0.1: `https://quality-software.dev/dim/v0.1`).
4. The DSSE signing key chain MUST be resolvable to an identity that asserts authority over the producer named in `producer.name`.
5. When `subject.layer` is `artifact`, `subject.digest` MUST be present and bind the manifest to the artifact via the in-toto Statement `subject` field.
6. When any `qualityAttributeClaim.status` is `verified`, at least one entry in `evidence[]` MUST be present for that claim.
7. When any `qualityAttributeClaim.status` is `declared` or `verified`, the `summary` field MUST be present and non-empty for that claim.
8. All URI fields (`evidence[].uri`, `informationalRefs[]`, `subject.sbomRef`, `subject.components[].manifestUri`, `industryRefs[].referenceUri`, `producer.contact` if a URI) MUST be syntactically valid URIs per [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986).
9. All `industryRefs[].standard` values MUST be interpretable as references to publicly identifiable standards. A bare numeric string (e.g., `"27001"`), an unqualified abbreviation (e.g., `"CSF"` without context), or a private vendor identifier is non-conforming.
10. `producer.issuedAt` MUST be a valid RFC 3339 / ISO 8601 timestamp not in the future relative to the producer's local clock at signing time.

A DIM is **strictly conforming** if, additionally:

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
- SHOULD re-issue the DIM when the underlying artifact's content digest changes. A DIM whose claims no longer match the artifact's current state is a correctness hazard.

### §5.3 Consumer responsibilities

A consumer of a DIM:

- MUST reject documents that fail items §5.1.1 (well-formed JSON), §5.1.2 (schema validation), §5.1.3 (DSSE envelope), §5.1.4 (signing identity), §5.1.5 (digest binding), §5.1.6 (evidence-when-verified), §5.1.7 (summary-when-declared-or-verified), or §5.1.10 (timestamp validity).
- SHOULD reject documents that fail items §5.1.8 (URI validity) or §5.1.9 (interpretable standard strings) unless operating in a trusted context where the producer is independently known.
- SHOULD warn when a DIM is conforming but not strictly conforming.
- MUST treat two DIMs with the same `subject.digest` and conflicting claims as an integrity failure requiring resolution before adoption.
- SHOULD consult `producer.validFor` to assess freshness. A DIM beyond its validity window MAY still be informative but SHOULD be treated as advisory only.
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

## Open issues

The following are deliberately deferred from this version of the specification:

- **DIM levels** (L0–L3) — a tiered conformance model analogous to SLSA build levels.
- **Authoring guide** — practical guidance for producers on what to populate per attribute and how to write honest summaries.
- **Verification guide** — practical guidance for consumers on how to evaluate a DIM in different decision contexts.
- **Lifecycle policy** — re-issuance, revocation, deprecation.
- **Vendor extension namespace** — the `x-*` key convention referenced in §5.1.12.
- **Stability annotations** per field — `stable | experimental | deprecated`.
- **Canonical-strings registry** — managed list of approved spellings for `industryRefs.standard` values.
- **Tension identifier registry** — the registry referenced in §5.1.11.
- **Conformance test suite** — corpus of known-good and known-bad manifests with expected validator outputs.

These will be addressed in subsequent iterations of this specification once §§1–5 stabilize.
