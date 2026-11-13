#!/usr/bin/env python3
"""Render the qualification Markdown report from structured result JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "qualification" / "templates" / "report.md"


def _status(level: dict) -> str:
    status = level.get("status", "missing")
    return {
        "pass": "PASS",
        "not-required": "N/R",
        "missing": "MISSING",
    }.get(status, status.upper())


def render(results: dict) -> str:
    rows = []
    image_sections = []
    for slug, case in results["cases"].items():
        levels = case["levels"]
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{slug}`",
                    case["status"].upper(),
                    _status(levels["q1"]),
                    _status(levels["q2"]),
                    _status(levels["q3"]),
                    _status(levels["q4"]),
                    _status(levels["q5"]),
                    _status(levels["q6"]),
                ]
            )
            + " |"
        )

        images = levels["q6"].get("images", [])
        if images:
            image_sections.append(f"### {case['title']} (`{slug}`)")
            image_sections.append("")
            image_sections.extend(
                f"- `../native/{slug}/{name}`"
                for name in images
            )
            image_sections.append("")

    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    return template.substitute(
        source_commit=results["source_commit"],
        solidcraft_version=results["solidcraft_version"],
        schema_version=results["schema_version"],
        case_rows="\n".join(rows),
        image_sections="\n".join(image_sections).rstrip() or "No native images were produced.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    results = json.loads(args.results.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(results), encoding="utf-8")
    print(f"Wrote qualification report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
