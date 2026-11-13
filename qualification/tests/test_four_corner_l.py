"""Qualification tests for four reusable L-profile feet under a frame."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class FourCornerLCommandTests(unittest.TestCase):
    def test_generated_bottom_face_placement_contract(self):
        document = run_script(
            ROOT / "examples/four-corner-l/scpf/model.py"
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
                ("frame_width", "120"),
                ("frame_depth", "80"),
            ],
        )

        components = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["FrameBlock", "CornerFoot"])

        copies = [
            row for row in commands
            if row["command"] == "occurrence.copy"
        ]
        self.assertEqual(len(copies), 3)
        self.assertTrue(
            all(row["params"]["component"] == "CornerFoot" for row in copies)
        )

        joints = [
            row["params"]
            for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 4)
        self.assertEqual(
            [joint["values"][2] for joint in joints],
            [0, 0, 0, 0],
        )

        expected_x = [
            [0.0, -1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
        ]
        for index, (joint, x_direction) in enumerate(
            zip(joints, expected_x),
            1,
        ):
            self.assertEqual(joint["type"], "planar")
            self.assertNotIn("offset", joint)
            self.assertEqual(joint["angle"], 0.0)
            self.assertEqual(
                joint["a"],
                {
                    "occurrence": "FrameBlock:1",
                    "point": [0.0, 0.0, 0.0],
                    "z": [0.0, 0.0, -1.0],
                    "x": [0.0, -1.0, 0.0],
                },
            )
            self.assertEqual(
                joint["b"],
                {
                    "occurrence": f"CornerFoot:{index}",
                    "point": [0.0, 0.0, 0.0],
                    "z": [0.0, 0.0, 1.0],
                    "x": x_direction,
                },
            )

        # Position is expressed in the parent BOTTOM face's local (u, v)
        # basis, not as world X/Y coordinates.
        self.assertEqual(
            [joint["values"] for joint in joints],
            [
                ["frame_depth / 2", "frame_width / 2", 0.0],
                ["frame_depth / 2", "-(frame_width / 2)", 0.0],
                ["-(frame_depth / 2)", "-(frame_width / 2)", 0.0],
                ["-(frame_depth / 2)", "frame_width / 2", 0.0],
            ],
        )
        self.assertFalse(
            any(
                row["command"] == "occurrence.move"
                and row["params"]["occurrence"].startswith("CornerFoot:")
                for row in commands
            )
        )


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class FourCornerLNativeTests(unittest.TestCase):
    def test_native_bounding_boxes_match_four_bottom_corner_feet(self):
        data = _load(
            Path(NATIVE_ROOT) / "four-corner-l" / "measurements.json"
        )
        self.assertEqual(data["body_count"], 5)

        frame = next(
            body for body in data["bodies"]
            if body["name"] == "FrameBlock"
        )
        self.assertEqual(
            _rounded_bbox(frame),
            {
                "min": [-60.0, -40.0, 0.0],
                "max": [60.0, 40.0, 60.0],
            },
        )

        feet = [
            body for body in data["bodies"]
            if body["name"].startswith("CornerFoot")
        ]
        self.assertEqual(len(feet), 4)

        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in feet
        )
        expected = sorted([
            ((-60.0, -40.0, -30.0), (-32.0, -12.0, 0.0)),
            ((32.0, -40.0, -30.0), (60.0, -12.0, 0.0)),
            ((32.0, 12.0, -30.0), (60.0, 40.0, 0.0)),
            ((-60.0, 12.0, -30.0), (-32.0, 40.0, 0.0)),
        ])
        self.assertEqual(actual, expected)

    def test_saved_size_mutation_moves_all_four_feet(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "four-corner-l"
            / "measurements-size-160x120.json"
        )
        self.assertEqual(data["body_count"], 5)
        self.assertEqual(
            _params(data),
            {
                "frame_width": 160.0,
                "frame_depth": 120.0,
            },
        )

        frame = next(
            body for body in data["bodies"]
            if body["name"] == "FrameBlock"
        )
        self.assertEqual(
            _rounded_bbox(frame),
            {
                "min": [-80.0, -60.0, 0.0],
                "max": [80.0, 60.0, 60.0],
            },
        )

        feet = [
            body for body in data["bodies"]
            if body["name"].startswith("CornerFoot")
        ]
        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in feet
        )
        expected = sorted([
            ((-80.0, -60.0, -30.0), (-52.0, -32.0, 0.0)),
            ((52.0, -60.0, -30.0), (80.0, -32.0, 0.0)),
            ((52.0, 32.0, -30.0), (80.0, 60.0, 0.0)),
            ((-80.0, 32.0, -30.0), (-52.0, 60.0, 0.0)),
        ])
        self.assertEqual(actual, expected)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _params(measurements):
    return {row["name"]: row["value"] for row in measurements["params"]}


def _rounded_bbox(body):
    return {
        "min": [round(value, 6) for value in body["bbox"]["min"]],
        "max": [round(value, 6) for value in body["bbox"]["max"]],
    }


if __name__ == "__main__":
    unittest.main()
