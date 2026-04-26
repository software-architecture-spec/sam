# SAM registries

Companion data files for the SAM specification. **Advisory only — not enforced by the JSON Schema.**

## Files

- **`standards.json`** — canonical spellings of common values for `industryRefs.standard` across SAM manifests. Lets producers pick a stable spelling and lets consumers normalize aliases when analyzing many manifests. Modeled on the SPDX License List pattern.
- **`tensions.json`** — well-known identifiers for `tensionsDeclared[].tension`, referenced from `SPECIFICATION.md §5.1.11`. Producers SHOULD use one of these IDs when the named tension applies; for domain-specific tensions, use the `x:` prefix.

## Why advisory, not enforced

Registries that are enforced by schema age poorly. New standards emerge faster than the SAM schema can churn; if `industryRefs.standard` were enum-restricted, every new ISO release would require a major version bump. The spec accepts free-text strings (§5.1.9) and adds this companion registry to reduce drift without locking the value space.

Tooling MAY:

- Suggest the canonical spelling when a producer uses an alias listed in `standards.json`.
- Normalize aliases when aggregating SAM data across many manifests.
- Surface unknown tension IDs for review (especially those not prefixed with `x:`).

Tooling MUST NOT reject a SAM solely because it uses an unregistered string in `industryRefs.standard` or `tensionsDeclared[].tension`.

## Shape

Both registries are flat JSON files with `registry`, `version`, `description`, and an `entries[]` array. Per-entry shapes:

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
