"""Qualification tests for one L-profile on all four front corners."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")

EXPECTED_CORNERS = [
    [-60.0, -15.0, 80.0],
    [60.0, -15.0, 80.0],
    [60.0, -15.0, 0.0],
    [-60.0, -15.0, 0.0],
]


class FourCornerLCommandTests(unittest.TestCase):
    def test_generated_corner_relationship_contract(self):
        document = run_script(
            ROOT / "examples/four-corner-l/scpf/model.py"
        )
        commands = document["commands"]

        self.assertFalse(
            any(row["command"] == "parameters.add" for row in commands)
        )

        components = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["FrameBlock", "LBracket"])

        copies = [
            row for row in commands
            if row["command"] == "occurrence.copy"
        ]
        self.assertEqual(len(copies), 3)
        self.assertTrue(
            all(row["params"]["component"] == "LBracket" for row in copies)
        )

        joints = [
            row["params"]
            for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 4)

        for index, (joint, corner) in enumerate(
            zip(joints, EXPECTED_CORNERS),
            1,
        ):
            self.assertEqual(joint["type"], "rigid")
            self.assertNotIn("offset", joint)
            self.assertNotIn("values", joint)
            self.assertEqual(joint["angle"], 0)
            self.assertEqual(joint["a"]["occurrence"], "FrameBlock:1")
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(
                joint["b"],
                {
                    "occurrence": f"LBracket:{index}",
                    "point": corner,
                    "z": [0, -1, 0],
                    "x": [1, 0, 0],
                },
            )


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class FourCornerLNativeTests(unittest.TestCase):
    def test_native_bounding_boxes_match_all_four_inward_corners(self):
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
                "min": [-60.0, -15.0, 0.0],
                "max": [60.0, 15.0, 80.0],
            },
        )

        brackets = [
            body for body in data["bodies"]
            if body["name"].startswith("LBracket")
        ]
        self.assertEqual(len(brackets), 4)

        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in brackets
        )
        expected = sorted([
            ((-60.0, -27.0, 40.0), (-20.0, -3.0, 80.0)),
            ((20.0, -27.0, 40.0), (60.0, -3.0, 80.0)),
            ((20.0, -27.0, 0.0), (60.0, -3.0, 40.0)),
            ((-60.0, -27.0, 0.0), (-20.0, -3.0, 40.0)),
        ])
        self.assertEqual(actual, expected)

    def test_native_joint_frames_rotate_consistently_around_corners(self):
        data = _load(
            Path(NATIVE_ROOT) / "four-corner-l" / "joint-inspect.json"
        )
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

        joints = data[0]["joints"]
        self.assertEqual(len(joints), 4)

        expected_parent_x = [
            [0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
        ]

        for joint, corner, parent_x in zip(
            joints,
            EXPECTED_CORNERS,
            expected_parent_x,
        ):
            self.assertEqual(joint["angle"], 0.0)
            self.assertEqual(joint["a"]["frame"]["origin"], corner)
            self.assertEqual(joint["a"]["frame"]["z"], [0.0, -1.0, 0.0])
            self.assertEqual(joint["a"]["frame"]["x"], parent_x)

            self.assertEqual(joint["b"]["frame"]["origin"], corner)
            self.assertEqual(joint["b"]["frame"]["z"], [0.0, 1.0, 0.0])
            self.assertEqual(joint["b"]["frame"]["x"], parent_x)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rounded_bbox(body):
    return {
        "min": [round(value, 6) for value in body["bbox"]["min"]],
        "max": [round(value, 6) for value in body["bbox"]["max"]],
    }


if __name__ == "__main__":
    unittest.main()
