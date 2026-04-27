# Contributing to SAM

SAM is a working-draft proposal. Breaking changes are expected. The stable target is **v1**. We are actively asking for technical review, authoring feedback, citations, and validator implementations — not adoption commitments.

This document covers how to engage. The normative reference is [`v0.2/SPECIFICATION.md`](v0.2/SPECIFICATION.md). Section numbers below refer to that document.

## What we're looking for

- **Technical review of the schema and spec** — places the model is wrong, ambiguous, or under-specified.
- **Real-world authoring feedback** — what's hard to populate? what's missing? what was confusing?
- **Citation and registry contributions** — entries for [`registry/standards.json`](registry/standards.json) and [`registry/tensions.json`](registry/tensions.json), or aliases for existing entries.
- **Validator implementations** — particularly for the spec-only conformance items (§5.1.6, §5.1.7, §5.1.9, §5.1.11) the JSON Schema can't enforce.

## How to engage

### Filing an issue

Use [Github Issues](https://github.com/software-architecture-spec/sam/issues) with predefined [issue templates](.github/ISSUE_TEMPLATE/). Pick the one that matches:

- **Schema change proposal** — for additions, removals, or rewordings of schema fields, conformance rules, or spec sections.
- **Registry addition** — for `standards.json` or `tensions.json` entries.
- **Bug report** — schema validation behaving unexpectedly, examples not validating, broken links, etc.
- **Real-world feedback** — share what you tried, what worked, what didn't.

Blank issues are disabled. If your concern doesn't fit a template, file under "Real-world feedback" and we'll re-categorize.

### Proposing a schema change

For non-trivial schema changes, **file an issue first**. Schema changes affect every published manifest's compatibility (per §6.3); discussion before code lowers the cost of getting it wrong.

Trivial fixes (typos, broken links, tightening a description without changing semantics) can come as direct PRs without a prior issue.

### Submitting a pull request

- **Small** (typo fix, prose clarification, registry alias addition): direct PR is fine.
- **Medium** (new conformance test case, anchor-table addition, README restructuring): linked issue preferred but not required.
- **Large** (schema change, new spec section, new normative requirement): linked issue **required**, with discussion landing first.

DCO sign-off is **not required** for v0. We will revisit if/when working-group adoption is on the table.

## Local validation

Every change touching `sam/`, `registry/`, or `tools/` must pass the repo validator before commit.

```sh
# One-time setup
pip install jsonschema

# Run all checks (schema metaschema, every version's examples, conformance corpus, registries)
python3 tools/validate.py
```

The validator is also wired into:

- **CI** — `.github/workflows/validate.yml` runs on every push and pull request to `main`.
- **An opt-in pre-commit hook** — enable for your clone with:

  ```sh
  git config core.hooksPath .githooks
  ```

  The hook only runs the validator when you stage relevant files; bypass with `git commit --no-verify` only when you understand what you're skipping.

## Pull request checklist

Before requesting review, confirm:

- [ ] `python3 tools/validate.py` passes locally
- [ ] If the schema changed: examples and conformance corpus updated to match
- [ ] If §5.1 conformance surface changed: corpus has positive and negative cases
- [ ] If a new spec section landed: cross-references resolve
- [ ] Linked issue (for medium/large changes)
- [ ] Commit message names the section / file affected and the rationale

## Versioning and frozen versions

`/v0.1/` is the current published version (and frozen at its URIs once any consumer signs against it). Changes go to the next minor (`v0.2` while `MAJOR` is `0`) or the next major. Past versions remain at their URIs forever — that's the same-MAJOR backward-compatibility promise (§6.3).

If you're proposing a change that would break a v0.1 manifest, label your issue `breaking` and explain the migration path. Whether the change lands in v0.x or waits for v1.0 depends on how disruptive it is; expect a discussion.

## Code of Conduct

This project adopts the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Be considerate; assume good faith; keep it about the work.

## Security

Security concerns about the spec, schema, or sample tooling go through [`SECURITY.md`](SECURITY.md), not the public issue tracker.

## Licensing of contributions

Contributions to the schema, examples, conformance corpus, registries, or sample tooling are accepted under the [Apache-2.0 license](LICENSE) the rest of the code uses. Contributions to specification text, README, or other prose are accepted under the [CC-BY-4.0 license](LICENSE-DOCS) for those files. Submitting a PR signals your acceptance of these terms.
