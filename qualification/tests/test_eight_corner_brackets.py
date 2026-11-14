"""Qualification tests for eight reusable outside L-brackets."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")

EXPECTED_CORNERS = [
    [-60.0, -40.0, 60.0],
    [60.0, -40.0, 60.0],
    [60.0, -40.0, 0.0],
    [-60.0, -40.0, 0.0],
    [-60.0, 40.0, 60.0],
    [60.0, 40.0, 60.0],
    [60.0, 40.0, 0.0],
    [-60.0, 40.0, 0.0],
]


class EightCornerBracketsCommandTests(unittest.TestCase):
    def test_generated_eight_corner_relationship_contract(self):
        document = run_script(
            ROOT / "examples/eight-corner-brackets/scpf/model.py"
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
                ("frame_height", "60"),
            ],
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
        self.assertEqual(len(copies), 7)
        self.assertTrue(
            all(row["params"]["component"] == "LBracket" for row in copies)
        )

        joints = [
            row["params"]
            for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 8)

        for index, (joint, corner) in enumerate(
            zip(joints, EXPECTED_CORNERS),
            1,
        ):
            self.assertEqual(joint["type"], "rigid")
            self.assertEqual(joint["angle"], 0)
            self.assertEqual(joint["a"]["occurrence"], "FrameBlock:1")
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(joint["b"]["occurrence"], f"LBracket:{index}")
            self.assertEqual(joint["b"]["z"], [0.0, -1.0, 0.0])
            self.assertEqual(joint["b"]["x"], [1.0, 0.0, 0.0])
            self.assertEqual(joint["offset"], -4.0)


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class EightCornerBracketsNativeTests(unittest.TestCase):
    def test_native_bounding_boxes_match_two_profiles_on_each_corner_line(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-corner-brackets"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 9)

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

        brackets = [
            body for body in data["bodies"]
            if body["name"].startswith("LBracket")
        ]
        self.assertEqual(len(brackets), 8)
        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in brackets
        )
        expected = sorted([
            ((-60.0, -40.0, 32.0), (-32.0, -36.0, 60.0)),
            ((32.0, -40.0, 32.0), (60.0, -36.0, 60.0)),
            ((32.0, -40.0, 0.0), (60.0, -36.0, 28.0)),
            ((-60.0, -40.0, 0.0), (-32.0, -36.0, 28.0)),
            ((-60.0, 36.0, 32.0), (-32.0, 40.0, 60.0)),
            ((32.0, 36.0, 32.0), (60.0, 40.0, 60.0)),
            ((32.0, 36.0, 0.0), (60.0, 40.0, 28.0)),
            ((-60.0, 36.0, 0.0), (-32.0, 40.0, 28.0)),
        ])
        self.assertEqual(actual, expected)

    def test_saved_size_mutation_moves_all_eight_brackets(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-corner-brackets"
            / "measurements-size-160x120x90.json"
        )
        self.assertEqual(data["body_count"], 9)
        self.assertEqual(
            _params(data),
            {
                "frame_width": 160.0,
                "frame_depth": 120.0,
                "frame_height": 90.0,
            },
        )

        brackets = [
            body for body in data["bodies"]
            if body["name"].startswith("LBracket")
        ]
        actual = sorted(
            (
                tuple(_rounded_bbox(body)["min"]),
                tuple(_rounded_bbox(body)["max"]),
            )
            for body in brackets
        )
        expected = sorted([
            ((-80.0, -60.0, 62.0), (-52.0, -56.0, 90.0)),
            ((52.0, -60.0, 62.0), (80.0, -56.0, 90.0)),
            ((52.0, -60.0, 0.0), (80.0, -56.0, 28.0)),
            ((-80.0, -60.0, 0.0), (-52.0, -56.0, 28.0)),
            ((-80.0, 56.0, 62.0), (-52.0, 60.0, 90.0)),
            ((52.0, 56.0, 62.0), (80.0, 60.0, 90.0)),
            ((52.0, 56.0, 0.0), (80.0, 60.0, 28.0)),
            ((-80.0, 56.0, 0.0), (-52.0, 60.0, 28.0)),
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
