# Security policy

## Scope

This policy covers security concerns about:

- The SAM **specification text** ([`v0.2/SPECIFICATION.md`](v0.2/SPECIFICATION.md) and prior versions) — design flaws that weaken the threat model.
- The **JSON Schema** ([`v0.2/schema.json`](v0.2/schema.json) and prior versions) — bugs that let invalid manifests pass or that reject conforming ones.
- The **sample tooling** in this repo — particularly [`tools/validate.py`](tools/validate.py) and the [`.github/workflows/validate.yml`](.github/workflows/validate.yml) CI workflow.
- The **registries** in [`registry/`](registry/) — incorrect or misleading canonical entries.

Out of scope for this policy:

- Third-party validator implementations and downstream tooling — report to the maintainer of the tool you're using.
- Operational consequences of using SAM in a deployed system — SAM declares producer intent; consequences of trusting a producer's claims are a consumer responsibility (see `SPECIFICATION.md §5.3`).
- Vulnerabilities in software whose SAM you're reading — report to that software's vendor; SAM itself is a manifest format.

## How to report

**Preferred:** [open a private security advisory](https://github.com/software-architecture-spec/software-architecture-spec.github.io/security/advisories/new) on this repository. GitHub routes the report privately to maintainers and provides a structured workspace for coordinated disclosure.

**Fallback:** if private advisories are unavailable to you, file a regular issue **without** technical details and ask for a private channel; a maintainer will route you to one.

Please **do not** open public issues for security concerns until coordinated disclosure has run its course.

## What to include

Helpful reports include:

- Affected file or section (e.g., "schema `qualityAttributeClaim.evidence`" or "spec §5.1.6")
- Affected version(s) (`v0.1`, working tree, future versions)
- The flaw — what's wrong, what attack or misuse it enables, what impact
- A demonstration if you have one (a manifest that exercises the flaw, a validator command that misbehaves)
- Your suggested fix (if any) — always welcome but not required

## Response

This is a working-draft project run by a small group; we make best-effort commitments only:

- **Acknowledgment** within 7 days of report.
- **Triage and initial assessment** within 14 days.
- **Coordinated disclosure** at a date agreed with the reporter, defaulting to 90 days from initial report or fix availability (whichever is earlier).

We do not offer bug bounties or have a CVE-issuing authority at v0.

## Versioning of fixes

Security-relevant fixes follow the same versioning rules as any other change (`SPECIFICATION.md §6`). A fix that requires a schema or spec change lands in the next minor; v0.x manifests already issued under affected versions remain at their frozen URIs but should be re-issued by their producers under the corrected version.

## Not a substitute for due diligence

Reading a SAM does not guarantee the producer's claims are accurate, complete, or current. SAM provides a structured surface for producer assertions; verification of those assertions against the consumer's risk tolerance is out of scope for this policy. See `SPECIFICATION.md §4.2 N1–N5` for the threats SAM does *not* defend against.
