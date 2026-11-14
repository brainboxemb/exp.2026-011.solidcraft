"""Qualification contract for assembly-owned named anchors."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class AssemblyOwnedAnchorCommandTests(unittest.TestCase):
    def test_named_assembly_anchor_resolves_to_native_corner_relationship(self):
        document = run_script(
            ROOT / "examples/assembly-owned-anchor/scpf/model.py"
        )
        commands = document["commands"]

        parameters = [
            row["params"]
            for row in commands
            if row["command"] == "parameters.add"
        ]
        self.assertEqual(
            [(row["name"], row["expression"]) for row in parameters],
            [
                ("base_width", "40"),
                ("base_height", "20"),
            ],
        )

        creates = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(creates, ["Base", "Companion", "Marker"])

        joints = [
            row["params"]
            for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 1)
        joint = joints[0]
        self.assertEqual(joint["type"], "rigid")
        self.assertEqual(
            joint["a"]["corner"],
            [20.0, -15.0, 20.0],
        )
        self.assertEqual(joint["a"]["occurrence"], "Base:1")
        self.assertEqual(joint["b"]["occurrence"], "Marker:1")


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class AssemblyOwnedAnchorNativeTests(unittest.TestCase):
    def test_baseline_named_anchor_geometry(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "assembly-owned-anchor"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 3)
        self.assertEqual(
            _bbox(_body(data, "Marker")),
            ([10.0, -25.0, 10.0], [20.0, -15.0, 20.0]),
        )

    def test_saved_resize_keeps_named_anchor_associative(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "assembly-owned-anchor"
            / "measurements-size-80x40.json"
        )
        self.assertEqual(
            {row["name"]: row["value"] for row in data["params"]},
            {"base_width": 80.0, "base_height": 40.0},
        )
        self.assertEqual(
            _bbox(_body(data, "Marker")),
            ([30.0, -25.0, 30.0], [40.0, -15.0, 40.0]),
        )


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _body(data, prefix):
    return next(
        body for body in data["bodies"]
        if body["name"].startswith(prefix)
    )


def _bbox(body):
    return (
        [round(value, 6) for value in body["bbox"]["min"]],
        [round(value, 6) for value in body["bbox"]["max"]],
    )


if __name__ == "__main__":
    unittest.main()
