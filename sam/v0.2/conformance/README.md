# SAM v0.2 conformance test corpus

A corpus of known-good (`pass-*.json`) and known-bad (`fail-*.json`) manifests indexed by `manifest.json`. Each case maps to one or more conformance items in `SPECIFICATION.md §5.1`.

## Index format

`manifest.json` lists each case with:

- `id` — stable identifier
- `file` — path relative to this directory
- `expected` — see "Outcome categories" below
- `covers` — `§5.1` items the case exercises
- `enforcedBy` — what tier of validator catches the violation
- `notes` — short description

## Outcome categories

| `expected` | Meaning |
|---|---|
| `valid` | Schema-valid AND spec-conforming. A SAM-aware validator accepts. |
| `invalid` | Schema-invalid. Any JSON Schema 2020-12 validator rejects. |
| `schema-valid-but-spec-nonconforming` | Schema accepts, but the case violates a `§5.1` item the schema cannot enforce. A SAM-aware validator MUST surface the violation. |
| `format-dependent` | Schema rejection depends on whether the validator runs `format` assertion. JSON Schema 2020-12 makes `format` annotation-by-default; assertion requires explicit configuration. |

## What the schema cannot enforce

Three categories of violation slip past pure schema validation:

1. **Conditional requirements** — §5.1.6 (`evidence` required when `status: verified`) and §5.1.7 (`summary` required when `status: declared|verified`) are conditional on a sibling field's value. The schema does not yet encode these as `if/then` blocks; a SAM-aware validator MUST walk every `qualityAttributeClaim` and check.
2. **Semantic interpretation** — §5.1.9 (interpretable `industryRefs.standard`) and §5.1.11 (well-known or `x:`-prefixed `tensionsDeclared.tension`) require a value-space judgment the schema's free-text accepts. A SAM-aware validator SHOULD consult `/registry/standards.json` and `/registry/tensions.json` and warn on unrecognized free-text strings.
3. **Format validation under default JSON Schema 2020-12 semantics** — §5.1.8 (URI validity) and §5.1.10 (timestamp validity) declare `format: uri` and `format: date-time` in the schema, but format checking is annotation-only by default. To assert format, the validator must be configured with a format-aware checker (e.g., `jsonschema.FormatChecker()` with `rfc3987` and `rfc3339-validator` packages installed for full coverage).

## How to run

### Schema-only validation (Python `jsonschema`)

```python
import json
from jsonschema import Draft202012Validator, FormatChecker

schema = json.load(open("sam/v0.2/schema.json"))
idx = json.load(open("sam/v0.2/conformance/manifest.json"))
v = Draft202012Validator(schema, format_checker=FormatChecker())

for case in idx["cases"]:
    expected = case["expected"]
    try:
        inst = json.load(open(f"sam/v0.2/conformance/{case['file']}"))
    except json.JSONDecodeError:
        assert expected == "invalid", case["id"]
        continue
    errs = list(v.iter_errors(inst))
    schema_valid = not errs
    if expected == "valid":
        assert schema_valid, (case["id"], errs[:1])
    elif expected == "invalid":
        assert not schema_valid, case["id"]
    elif expected == "schema-valid-but-spec-nonconforming":
        assert schema_valid, (case["id"], errs[:1])
    # format-dependent: either outcome accepted
```

### Spec-aware validation (sketch)

A future SAM-aware validator should additionally walk:

- Every `qualityAttributeClaim` (top-level `qualityAttributes.*.overall`, every `subCharacteristics.*`, every entry under `extensions`):
  - If `status == "verified"` and `evidence` is empty/missing → §5.1.6 violation.
  - If `status in ("declared", "verified")` and `summary` is missing/empty → §5.1.7 violation.
- Every `industryRefs[].standard` against `/registry/standards.json` aliases → suggest canonical or warn on bare numeric.
- Every `tensionsDeclared[].tension` against `/registry/tensions.json`; flag unknown values without an `x:` prefix as §5.1.11 strict-conformance violations.
- `producer.issuedAt + producer.validFor` against the current time → §5.1.13 strict-conformance check.

The conformance corpus exercises each of these items so spec-aware validators can be tested against the same fixtures.

## Adding cases

Add a JSON file (`pass-*.json` or `fail-*.json`), then add an entry to `manifest.json` with the right `expected`, `covers`, `enforcedBy`, and `notes`. Run the corpus runner above to confirm the index is consistent with actual schema behavior.

## Out of scope (no fixtures)

- §5.1.3 (DSSE envelope) — out-of-band, signing-tool concern.
- §5.1.4 (signing identity) — same.
- §5.1.13 (validFor freshness) — runtime check; a fixture would only verify the field is present, which is covered by `pass-strict-validfor.json`.
