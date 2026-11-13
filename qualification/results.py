#!/usr/bin/env python3
"""Collect qualification outputs into stable per-case JSON results.

This module does not run CAD operations itself. It normalizes evidence already
produced by the Python tests and native SolidCraft qualification workflow so
Pages, CI summaries and future tooling can consume the same result contract.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

from qualification_cases import QUALIFICATION_CASES


SCHEMA_VERSION = 1


def _read_tsv(path: Path, key: str = "case") -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            row[key]: row
            for row in csv.DictReader(handle, delimiter="\t")
            if row.get(key)
        }


def _suite_passed(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "\nOK\n" in f"\n{text}\n" or text.rstrip().endswith("OK")


def _existing_names(case_dir: Path, patterns: tuple[str, ...]) -> list[str]:
    names: set[str] = set()
    for pattern in patterns:
        names.update(path.name for path in case_dir.glob(pattern) if path.is_file() and path.stat().st_size)
    return sorted(names)


def collect(
    qualification_dir: Path,
    native_root: Path,
    source_commit: str,
    solidcraft_version: str,
) -> dict:
    q1_pass = _suite_passed(qualification_dir / "q1-python-tests.txt")
    q2_tests_pass = _suite_passed(qualification_dir / "q2-python-qualification-tests.txt")
    native_tests_pass = _suite_passed(qualification_dir / "q3-q5-python-qualification-tests.txt")

    q2_rows = _read_tsv(qualification_dir / "q2-command-contract.tsv")
    native_rows = _read_tsv(qualification_dir / "q3-q4-q6-native.tsv")
    mutation_rows = _read_tsv(qualification_dir / "q5-parametric-mutation.tsv")

    aggregate = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "solidcraft_version": solidcraft_version,
        "cases": {},
    }

    for case in QUALIFICATION_CASES:
        slug = case["slug"]
        case_dir = native_root / slug
        q2 = q2_rows.get(slug, {})
        native = native_rows.get(slug, {})
        mutation = mutation_rows.get(slug)
        mutation_required = bool(case.get("q5_required", False))

        images = _existing_names(case_dir, ("model*.png",))
        native_files = _existing_names(
            case_dir,
            (
                "results*.json",
                "measurements*.json",
                "change-*.json",
                "parameters*.json",
                "joint-*.json",
                "model.json",
                "model*.sc",
                "model*.step",
                "export-*.json",
            ),
        )

        q2_pass = q2_tests_pass and q2.get("status") == "PASS"
        q3_pass = native.get("build") == "PASS"
        q4_pass = native.get("eval") == "PASS" and native_tests_pass
        q6_pass = native.get("snapshot") == "PASS" and bool(images)
        if mutation_required:
            q5_status = "pass" if mutation and mutation.get("status") == "PASS" and native_tests_pass else "missing"
        else:
            q5_status = "not-required"

        levels = {
            "q1": {
                "status": "pass" if q1_pass else "missing",
                "evidence": ["q1-python-tests.txt"] if q1_pass else [],
            },
            "q2": {
                "status": "pass" if q2_pass else "missing",
                "commands": int(q2["commands"]) if q2.get("commands", "").isdigit() else None,
                "evidence": ["q2-python-qualification-tests.txt", "q2-command-contract.tsv"] if q2_pass else [],
            },
            "q3": {
                "status": "pass" if q3_pass else "missing",
                "evidence": [name for name in native_files if name in {"results.json", "model.sc", "model.step"}],
            },
            "q4": {
                "status": "pass" if q4_pass else "missing",
                "evidence": [name for name in native_files if name.startswith("measurements") or name.startswith("joint-")],
            },
            "q5": {
                "status": q5_status,
                "required": mutation_required,
                "mutation": mutation.get("mutation") if mutation else None,
                "evidence": [
                    name for name in native_files
                    if name.startswith("change-") or "size-" in name or "width-" in name
                    or "gap-" in name or "shift-" in name or "shared-width-" in name
                ],
            },
            "q6": {
                "status": "pass" if q6_pass else "missing",
                "images": images,
            },
        }

        required_statuses = [
            level["status"]
            for key, level in levels.items()
            if key != "q5" or mutation_required
        ]
        overall = "pass" if all(status == "pass" for status in required_statuses) else "incomplete"

        result = {
            "schema_version": SCHEMA_VERSION,
            "case": slug,
            "title": case["title"],
            "source_commit": source_commit,
            "solidcraft_version": solidcraft_version,
            "status": overall,
            "levels": levels,
            "evidence": {
                "native_files": native_files,
                "images": images,
            },
        }
        aggregate["cases"][slug] = result

        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "qualification-result.json").write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )

    qualification_dir.mkdir(parents=True, exist_ok=True)
    (qualification_dir / "results.json").write_text(
        json.dumps(aggregate, indent=2) + "\n",
        encoding="utf-8",
    )
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualification-dir", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--solidcraft-version", required=True)
    args = parser.parse_args()

    aggregate = collect(
        args.qualification_dir,
        args.native_root,
        args.source_sha,
        args.solidcraft_version,
    )
    incomplete = [
        slug for slug, result in aggregate["cases"].items()
        if result["status"] != "pass"
    ]
    if incomplete:
        print("Incomplete qualification cases: " + ", ".join(incomplete), file=sys.stderr)
        return 1
    print(f"Collected {len(aggregate['cases'])} qualification case results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
