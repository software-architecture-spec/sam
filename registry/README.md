# SAM registries

Companion data files for the SAM specification. **Advisory only — not enforced by the JSON Schema.**

## Files

- **`standards.json`** — canonical spellings of common values for `industryRefs.standard` across SAM manifests. Lets producers pick a stable spelling and lets consumers normalize aliases when analyzing many manifests. Modeled on the SPDX License List pattern.
- **`tensions.json`** — well-known identifiers for `tensionsDeclared[].tension`, referenced from `SPECIFICATION.md §5.1.11`. Producers SHOULD use one of these IDs when the named tension applies; for domain-specific tensions, use the `x:` prefix.
- **`delivery-forms.json`** — canonical identifiers for how software is delivered and who operates it (`saas`, `self_hosted_service`, `library`, `cli_tool`, `desktop_app`, `mobile_app`, `browser_extension`, `infrastructure`, `appliance`). Referenced from `SPECIFICATION.md §10`, where the delivery form governs how a quality claim reads — the same key asserts a measured SLO for producer-operated software and a default-plus-sizing-guidance for consumer-operated software. Used by `intent.deliveryForm` and `envelope.dependencies[].deliveryForm` (v0.3), which share this one vocabulary; a dependency additionally carries `role` (the functional axis that v0.2's `dependencies[].type` mixed in, split apart in v0.3). Source model (proprietary / open_source / source_available) is an orthogonal axis, not a delivery form.
- **`patterns.json`** — well-known identifiers for `intent.architecturalPatterns[]` (`circuit_breaker`, `bulkhead`, `saga`, `cqrs`, `event_sourcing`, `outbox`, `repository`, …). Producers SHOULD use a registered ID when the pattern applies; for project-specific patterns, use the `x:` prefix. Advisory — the field is an open string array.

## Why advisory, not enforced

Registries that are enforced by schema age poorly. New standards emerge faster than the SAM schema can churn; if `industryRefs.standard` were enum-restricted, every new ISO release would require a major version bump. The spec accepts free-text strings (§5.1.9) and adds this companion registry to reduce drift without locking the value space.

Tooling MAY:

- Suggest the canonical spelling when a producer uses an alias listed in `standards.json`.
- Normalize aliases when aggregating SAM data across many manifests.
- Surface unknown tension IDs for review (especially those not prefixed with `x:`).

Tooling MUST NOT reject a SAM solely because it uses an unregistered string in `industryRefs.standard` or `tensionsDeclared[].tension`.

## Shape

The registries are flat JSON files with `registry`, `version`, `description`, and an `entries[]` array. Per-entry shapes:

**`standards.json` entry:**

```json
{ "canonical": "...", "aliases": ["..."], "uri": "...", "domain": "..." }
```

`canonical` is the spelling SAM-aware tooling will treat as authoritative. `aliases` lists known variations that should map to the canonical. `uri` points at the canonical authoritative source for the standard. `domain` is a free-text categorization for filtering.

**`tensions.json` entry:**

```json
{ "id": "...", "name": "...", "summary": "...", "cite": "...", "uri": "...", "applies_to": ["..."] }
```

`id` is the value that goes in `tensionsDeclared[].tension`. `name`, `summary`, and `cite` describe the tension to humans and auditors. `applies_to` names the SAM `qualityAttributes` characteristics or `extensions` that the tension typically couples.

**`delivery-forms.json` entry:**

```json
{ "id": "...", "name": "...", "aka": ["..."], "operator": "producer|consumer|shared", "typical_layers": ["..."], "perimeter_owner": "...", "claims_read_as": "..." }
```

`id` is the canonical delivery-form identifier (the value for `intent.deliveryForm` and `envelope.dependencies[].deliveryForm`, v0.3). `aka` lists common names that map to it (e.g. `SaaS`, `COTS`, `SDK`). `operator` is who runs the software (`producer`, `consumer`, or `shared`). `typical_layers` names the `subject.layer` values the form usually appears at. `perimeter_owner` names who owns the security/operational boundary. `claims_read_as` explains, for authors, how §10 quality claims should be interpreted for that form.

**`patterns.json` entry:** same shape as `tensions.json` (`id`, `name`, `summary`, `cite`, `uri`, `applies_to`). `id` is the value that goes in `intent.architecturalPatterns[]`; `applies_to` names the `qualityAttributes` the pattern typically serves.

## Versioning

Each registry declares its own `version` independent of the SAM specification version. Registry versions follow SemVer at registry granularity:

- **PATCH** — typo fixes, URI updates that resolve to the same content, alias additions.
- **MINOR** — new entries.
- **MAJOR** — breaking changes (renaming a `canonical` or `id`, removing entries). Avoided where possible — past values must remain interpretable.

A registry's `version` does not change the SAM `manifestVersion`. SAMs reference standards and tensions by string; the registry is a translation aid, not a normative dependency.

## Contributing

Open an issue or PR at the SAM repo with:

- The proposed canonical spelling (for `standards.json`) or tension ID (for `tensions.json`).
- A canonical reference URI.
- A short justification: where the standard/tension is used in real SAM manifests, and which `domain` or `applies_to` it belongs in.

Aliases for existing entries are welcome — they lower the cost of producer drift.
