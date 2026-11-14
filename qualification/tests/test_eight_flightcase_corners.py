"""Qualification contract for eight trihedral flightcase corners."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class EightFlightcaseCornersCommandTests(unittest.TestCase):
    def test_all_eight_3d_corners_reuse_one_component(self):
        commands = run_script(
            ROOT / "examples/eight-flightcase-corners/scpf/model.py"
        )["commands"]

        parameters = [
            row["params"]
            for row in commands
            if row["command"] == "parameters.add"
        ]
        self.assertEqual(
            [(row["name"], row["expression"]) for row in parameters],
            [
                ("case_width", "120"),
                ("case_depth", "80"),
                ("case_height", "60"),
            ],
        )

        components = [
            row["params"]["name"] for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["CaseBlock", "FlightcaseCorner"])
        self.assertEqual(
            len([row for row in commands if row["command"] == "occurrence.copy"]),
            7,
        )

        fillets = [
            row["params"]
            for row in commands
            if row["command"] == "solid.fillet"
        ]
        self.assertEqual(len(fillets), 1)
        self.assertEqual(float(fillets[0]["radius"]), 8.0)

        joints = [
            row["params"] for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 8)

        expected_xy = [
            ("-(case_width / 2)", "-(case_depth / 2)"),
            ("case_width / 2", "-(case_depth / 2)"),
            ("case_width / 2", "case_depth / 2"),
            ("-(case_width / 2)", "case_depth / 2"),
            ("-(case_width / 2)", "-(case_depth / 2)"),
            ("case_width / 2", "-(case_depth / 2)"),
            ("case_width / 2", "case_depth / 2"),
            ("-(case_width / 2)", "case_depth / 2"),
        ]
        expected_child_frames = [
            ([0.0, 0.0, -1.0], [1.0, 0.0, 0.0]),
            ([0.0, 0.0, -1.0], [0.0, -1.0, 0.0]),
            ([0.0, 0.0, -1.0], [-1.0, 0.0, 0.0]),
            ([0.0, 0.0, -1.0], [0.0, 1.0, 0.0]),
            ([0.0, 0.0, 1.0], [0.0, 1.0, 0.0]),
            ([0.0, 0.0, 1.0], [-1.0, 0.0, 0.0]),
            ([0.0, 0.0, 1.0], [0.0, -1.0, 0.0]),
            ([0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        ]

        for index, joint in enumerate(joints, 1):
            self.assertEqual(joint["type"], "planar")
            self.assertEqual(joint["angle"], 0.0)
            self.assertEqual(
                joint["a"],
                {
                    "occurrence": "CaseBlock:1",
                    "point": [0.0, 0.0, 0.0],
                    "z": [0.0, 0.0, 1.0],
                    "x": [1.0, 0.0, 0.0],
                },
            )
            self.assertEqual(
                tuple(joint["values"][:2]),
                expected_xy[index - 1],
            )
            self.assertEqual(joint["values"][2], 0.0)
            self.assertEqual(
                joint["b"]["occurrence"],
                f"FlightcaseCorner:{index}",
            )
            z, x = expected_child_frames[index - 1]
            self.assertEqual(joint["b"]["z"], z)
            self.assertEqual(joint["b"]["x"], x)

        for joint in joints[:4]:
            self.assertNotIn("offset", joint)
        for joint in joints[4:]:
            self.assertEqual(joint["offset"], "case_height")


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class EightFlightcaseCornersNativeTests(unittest.TestCase):
    def test_native_bounds_wrap_all_eight_case_corners(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-flightcase-corners"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 9)

        protectors = _protectors(data)
        self.assertEqual(len(protectors), 8)
        self.assertEqual(
            sorted(_body_size(body) for body in protectors),
            [(24.0, 24.0, 24.0)] * 8,
        )

        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in protectors
        )
        expected = sorted([
            ((-64.0, -44.0, -4.0), (-40.0, -20.0, 20.0)),
            ((40.0, -44.0, -4.0), (64.0, -20.0, 20.0)),
            ((40.0, 20.0, -4.0), (64.0, 44.0, 20.0)),
            ((-64.0, 20.0, -4.0), (-40.0, 44.0, 20.0)),
            ((-64.0, -44.0, 40.0), (-40.0, -20.0, 64.0)),
            ((40.0, -44.0, 40.0), (64.0, -20.0, 64.0)),
            ((40.0, 20.0, 40.0), (64.0, 44.0, 64.0)),
            ((-64.0, 20.0, 40.0), (-40.0, 44.0, 64.0)),
        ])
        self.assertEqual(actual, expected)

    def test_saved_size_mutation_moves_but_does_not_resize_protectors(self):
        baseline = _load(
            Path(NATIVE_ROOT)
            / "eight-flightcase-corners"
            / "measurements.json"
        )
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-flightcase-corners"
            / "measurements-size-160x120x90.json"
        )
        self.assertEqual(data["body_count"], 9)
        self.assertEqual(
            {row["name"]: row["value"] for row in data["params"]},
            {
                "case_width": 160.0,
                "case_depth": 120.0,
                "case_height": 90.0,
            },
        )
        self.assertEqual(
            sorted(_body_size(body) for body in _protectors(data)),
            sorted(_body_size(body) for body in _protectors(baseline)),
        )
        self.assertEqual(
            sorted(_body_size(body) for body in _protectors(data)),
            [(24.0, 24.0, 24.0)] * 8,
        )


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _protectors(data):
    return [
        body for body in data["bodies"]
        if body["name"].startswith("FlightcaseCorner")
    ]


def _body_size(body):
    return tuple(
        round(hi - lo, 6)
        for lo, hi in zip(body["bbox"]["min"], body["bbox"]["max"])
    )


def _rounded_bbox(body):
    return {
        "min": [round(value, 6) for value in body["bbox"]["min"]],
        "max": [round(value, 6) for value in body["bbox"]["max"]],
    }


if __name__ == "__main__":
    unittest.main()
