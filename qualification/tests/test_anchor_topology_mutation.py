"""Qualification contract for native AnchorTopology mutation."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class AnchorTopologyMutationCommandTests(unittest.TestCase):
    def test_fixed_topology_pick_is_inlined(self):
        document = run_script(
            ROOT / "examples/anchor-topology-mutation/scpf/model.py"
        )
        commands = document["commands"]

        self.assertFalse(
            any(row["command"] == "joint.origin" for row in commands)
        )

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

        joint = next(
            row["params"]
            for row in commands
            if row["command"] == "joint.create"
        )
        self.assertEqual(
            joint["a"],
            {
                "occurrence": "Board:1",
                "edge": [-20.0, -10.0, 10.0],
                "on": [0.0, -10.0, 10.0],
                "corner": [-20.0, -10.0, 20.0],
                "z": [0.0, -1.0, 0.0],
                "x": [0.0, 0.0, -1.0],
            },
        )
        self.assertEqual(joint["b"]["occurrence"], "Marker:1")
        self.assertEqual(joint["b"]["point"], [0.0, 0.0, 0.0])


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class AnchorTopologyMutationNativeTests(unittest.TestCase):
    def test_baseline_marker_is_on_selected_corner(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "anchor-topology-mutation"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 2)
        self.assertEqual(
            _bbox(_body(data, "Board")),
            ([-20.0, -10.0, 0.0], [20.0, 10.0, 20.0]),
        )
        self.assertEqual(
            _bbox(_body(data, "Marker")),
            ([-25.0, -15.0, 15.0], [-15.0, -5.0, 25.0]),
        )

    def test_saved_resize_moves_marker_with_same_native_topology(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "anchor-topology-mutation"
            / "measurements-size-80x40.json"
        )
        self.assertEqual(
            {row["name"]: row["value"] for row in data["params"]},
            {"base_width": 80.0, "base_height": 40.0},
        )
        self.assertEqual(
            _bbox(_body(data, "Board")),
            ([-40.0, -10.0, 0.0], [40.0, 10.0, 40.0]),
        )
        self.assertEqual(
            _bbox(_body(data, "Marker")),
            ([-45.0, -15.0, 35.0], [-35.0, -5.0, 45.0]),
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
