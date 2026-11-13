#!/usr/bin/env python3
"""Assertions for the parameter-scope qualification case.

The workflow orchestrates SolidCraft. Functional expectations live here so
Q2/Q5 semantics stay beside the case rather than becoming shell/JQ folklore.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_SOLIDCRAFT_VERSION = "0.30.1"


def _load(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _parameter_commands(document):
    return [
        row["params"]
        for row in document["commands"]
        if row["command"] == "parameters.add"
    ]


def check_command_document(document):
    params = _parameter_commands(document)
    assert [(row["name"], row["expression"]) for row in params] == [
        ("Panel_width", "40"),
        ("Panel_2_width", "60"),
        ("shared_width", "80"),
    ], params

    rectangles = [
        row["params"]
        for row in document["commands"]
        if row["command"] == "sketch.rectangle.two_point"
    ]
    assert len(rectangles) == 4, rectangles

    x_expressions = [(row["p0"][0], row["p1"][0]) for row in rectangles]
    assert ("-Panel_width / 2", "Panel_width / 2") in x_expressions
    assert ("-Panel_2_width / 2", "Panel_2_width / 2") in x_expressions
    assert ("-shared_width / 2", "shared_width / 2") in x_expressions

    derived = [
        pair for pair in x_expressions
        if "shared_width / 2" in str(pair[0])
        and "shared_width / 2" in str(pair[1])
        and pair != ("-shared_width / 2", "shared_width / 2")
    ]
    assert len(derived) == 1, x_expressions

    creates = [
        row["params"]["name"]
        for row in document["commands"]
        if row["command"] == "component.create"
    ]
    assert creates == ["Panel", "Panel 2", "Panel 3", "Panel 4"], creates

    copies = [
        row for row in document["commands"]
        if row["command"] == "occurrence.copy"
    ]
    assert len(copies) == 1, copies


def check_commands(path):
    check_command_document(_load(path))


def _widths(measurements):
    return sorted(
        round(body["bbox"]["max"][0] - body["bbox"]["min"][0], 6)
        for body in measurements["bodies"]
    )


def _params(measurements):
    return {row["name"]: row["value"] for row in measurements["params"]}


def check_baseline(measurements_path, parameters_path, model_json_path, version):
    assert version == EXPECTED_SOLIDCRAFT_VERSION, (
        f"case evidence is version-specific: expected "
        f"{EXPECTED_SOLIDCRAFT_VERSION}, got {version}"
    )

    measurements = _load(measurements_path)
    assert measurements["body_count"] == 5
    assert _widths(measurements) == [40.0, 40.0, 60.0, 80.0, 80.0]

    params = _params(measurements)
    assert params == {
        "Panel_width": 40.0,
        "Panel_2_width": 60.0,
        "shared_width": 80.0,
    }, params

    exported = _load(parameters_path)
    exported_names = {row["name"] for row in exported}
    assert exported_names == set(params), exported

    # Keep the design JSON as evidence, but do not bind Forge to SolidCraft's
    # private internal schema. Only assert that this runtime produced a valid
    # versioned SolidCraft design document.
    design = _load(model_json_path)
    assert isinstance(design, dict)
    fmt = design.get("format")
    assert isinstance(fmt, str) and fmt.startswith("solidcraft/"), fmt


def check_shared_mutation(measurements_path):
    measurements = _load(measurements_path)
    params = _params(measurements)
    assert params["Panel_width"] == 40.0
    assert params["Panel_2_width"] == 60.0
    assert params["shared_width"] == 100.0

    assert _widths(measurements) == [40.0, 50.0, 60.0, 100.0, 100.0]


def write_native_commands(directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)

    (root / "export-parameters.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "parameters.export",
                        "params": {
                            "format": "json",
                            "path": str(root / "parameters.json"),
                        },
                    }
                ]
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    (root / "change-shared-width.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "parameters.change",
                        "params": {
                            "name": "shared_width",
                            "expression": "100 mm",
                        },
                    }
                ]
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    q2 = sub.add_parser("commands")
    q2.add_argument("path")

    prepare = sub.add_parser("prepare-native")
    prepare.add_argument("directory")

    base = sub.add_parser("baseline")
    base.add_argument("measurements")
    base.add_argument("parameters")
    base.add_argument("model_json")
    base.add_argument("--solidcraft-version", required=True)

    changed = sub.add_parser("shared-mutation")
    changed.add_argument("measurements")

    args = parser.parse_args()
    if args.command == "commands":
        check_commands(args.path)
    elif args.command == "prepare-native":
        write_native_commands(args.directory)
    elif args.command == "baseline":
        check_baseline(
            args.measurements,
            args.parameters,
            args.model_json,
            args.solidcraft_version,
        )
    elif args.command == "shared-mutation":
        check_shared_mutation(args.measurements)


if __name__ == "__main__":
    main()
