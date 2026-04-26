---
name: Bug report
about: Schema validating something it shouldn't, examples not validating, broken links, validator misbehaving
title: "[bug] "
labels: ["bug"]
---

<!--
For security-related bugs, do NOT file here. See SECURITY.md for the private reporting path.
-->

## Affected file or section

Path + line/section number. e.g., `sam/v0.2/schema.json` (qualityAttributeClaim.evidence), or `sam/v0.2/SPECIFICATION.md §5.1.6`.

## Affected version

- [ ] `v0.1` (frozen)
- [ ] `v0.2` (current)
- [ ] working tree (`main` branch ahead of latest tagged)

## Expected behavior

What should happen?

## Actual behavior

What happens?

## Reproduction steps

If schema-related, include the smallest manifest snippet that reproduces. If validator-related, include the exact command and the validator version (`pip show jsonschema`).

```json
// minimal repro manifest
```

```sh
# command that misbehaves
python3 tools/validate.py
```

## Environment

- Python version: `python3 --version`
- jsonschema version: `pip show jsonschema | grep Version`
- OS: macOS / Linux / Windows
