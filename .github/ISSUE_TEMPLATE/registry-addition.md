---
name: Registry addition
about: Propose a new entry or alias for registry/standards.json or registry/tensions.json
title: "[registry] "
labels: ["registry", "proposal"]
---

<!--
The registries are advisory, not enforced by the schema. Read registry/README.md first.
-->

## Which registry?

- [ ] `registry/standards.json` — canonical spelling for `industryRefs.standard`
- [ ] `registry/tensions.json` — well-known ID for `tensionsDeclared[].tension`

## Proposed entry

For `standards.json`:

```json
{
  "canonical": "...",
  "aliases": ["...", "..."],
  "uri": "...",
  "domain": "..."
}
```

For `tensions.json`:

```json
{
  "id": "...",
  "name": "...",
  "summary": "...",
  "cite": "...",
  "uri": "...",
  "applies_to": ["..."]
}
```

## Justification

Where have you seen this used? Real SAM manifests, internal use, industry context — concrete examples help reviewers evaluate canonical-vs-alias decisions.

## Source URLs

The authoritative source for the standard or tension. For `standards.json`, this is typically the standards body (ISO, NIST, OWASP, IETF, etc.). For `tensions.json`, an academic paper or established industry writeup.

## Additional context

If this is an alias for an existing entry, just state the canonical and the alias. If it's a new canonical, briefly note the domain it should fall under.
