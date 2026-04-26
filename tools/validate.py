#!/usr/bin/env python3
"""
SAM repo validator.

Runs every check the spec promises: schema metaschema validation, all example
manifests against their schemas, the conformance corpus per its index, and
registry JSON parses. Used by the git pre-commit hook and CI.

Exit codes:
    0  all checks passed
    1  one or more checks failed
    2  prerequisite missing (jsonschema not installed, etc.)

Usage:
    python3 tools/validate.py            # full check
    python3 tools/validate.py --quiet    # only print failures + summary
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent

QUIET = "--quiet" in sys.argv

failures: list[str] = []
checks_run = 0


def log(msg: str) -> None:
    if not QUIET:
        print(msg)


def fail(label: str, detail: str) -> None:
    failures.append(f"{label}: {detail}")
    print(f"FAIL {label}: {detail}", file=sys.stderr)


def check_schema_versions() -> None:
    """Each version's schema validates against the JSON Schema 2020-12 metaschema."""
    global checks_run
    for version_dir in sorted(REPO.glob("v*/")):
        schema_path = version_dir / "schema.json"
        if not schema_path.exists():
            continue
        checks_run += 1
        try:
            schema = json.loads(schema_path.read_text())
            Draft202012Validator.check_schema(schema)
            log(f"PASS schema-metaschema: {schema_path.relative_to(REPO)}")
        except Exception as e:
            fail(f"schema-metaschema {schema_path.relative_to(REPO)}", str(e))


def check_examples() -> None:
    """Every version's examples validate against that version's schema."""
    global checks_run
    for version_dir in sorted(REPO.glob("v*/")):
        schema_path = version_dir / "schema.json"
        ex_dir = version_dir / "examples"
        if not (schema_path.exists() and ex_dir.is_dir()):
            continue
        try:
            schema = json.loads(schema_path.read_text())
        except Exception as e:
            fail(f"schema-load {schema_path.relative_to(REPO)}", str(e))
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for ex_path in sorted(ex_dir.glob("*.json")):
            checks_run += 1
            try:
                inst = json.loads(ex_path.read_text())
            except json.JSONDecodeError as e:
                fail(f"example-parse {ex_path.relative_to(REPO)}", str(e))
                continue
            errs = list(validator.iter_errors(inst))
            if errs:
                msg = errs[0].message[:160]
                fail(f"example-validate {ex_path.relative_to(REPO)}", msg)
            else:
                log(f"PASS example: {ex_path.relative_to(REPO)}")


def check_conformance_corpus() -> None:
    """Run each conformance case and confirm actual outcome matches expected."""
    global checks_run
    for version_dir in sorted(REPO.glob("v*/")):
        conf_dir = version_dir / "conformance"
        idx_path = conf_dir / "manifest.json"
        schema_path = version_dir / "schema.json"
        if not (idx_path.exists() and schema_path.exists()):
            continue
        try:
            schema = json.loads(schema_path.read_text())
            idx = json.loads(idx_path.read_text())
        except Exception as e:
            fail(f"corpus-load {idx_path.relative_to(REPO)}", str(e))
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())

        for case in idx["cases"]:
            checks_run += 1
            case_path = conf_dir / case["file"]
            expected = case["expected"]

            try:
                inst = json.loads(case_path.read_text())
                json_ok = True
            except json.JSONDecodeError:
                json_ok = False
                inst = None

            if not json_ok:
                if expected == "invalid":
                    log(f"PASS conformance/{case['id']}: parse-fail (expected invalid)")
                else:
                    fail(f"conformance/{case['id']}", f"parse-fail; expected {expected}")
                continue

            errs = list(validator.iter_errors(inst))
            schema_valid = not errs

            if expected == "valid":
                if schema_valid:
                    log(f"PASS conformance/{case['id']}")
                else:
                    fail(f"conformance/{case['id']}", f"expected valid; got: {errs[0].message[:120]}")
            elif expected == "invalid":
                if not schema_valid:
                    log(f"PASS conformance/{case['id']}: rejected")
                else:
                    fail(f"conformance/{case['id']}", "expected invalid; schema accepted")
            elif expected == "schema-valid-but-spec-nonconforming":
                if schema_valid:
                    log(f"PASS conformance/{case['id']}: schema-valid (spec rejects)")
                else:
                    fail(
                        f"conformance/{case['id']}",
                        f"expected schema-valid-but-spec-nonconforming; schema rejected: {errs[0].message[:120]}",
                    )
            elif expected == "format-dependent":
                # Either outcome is acceptable; format checking is implementation-defined
                log(f"PASS conformance/{case['id']}: format-dependent (schema_valid={schema_valid})")
            else:
                fail(f"conformance/{case['id']}", f"unknown 'expected' value: {expected}")


def check_registries() -> None:
    """Registry JSON files parse cleanly."""
    global checks_run
    reg_dir = REPO / "registry"
    if not reg_dir.is_dir():
        return
    for reg_path in sorted(reg_dir.glob("*.json")):
        checks_run += 1
        try:
            json.loads(reg_path.read_text())
            log(f"PASS registry-parse: {reg_path.relative_to(REPO)}")
        except json.JSONDecodeError as e:
            fail(f"registry-parse {reg_path.relative_to(REPO)}", str(e))


def main() -> int:
    log("== SAM repo validator ==")
    check_schema_versions()
    check_examples()
    check_conformance_corpus()
    check_registries()

    print()
    if failures:
        print(f"FAILED: {len(failures)} of {checks_run} checks", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"OK: all {checks_run} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
