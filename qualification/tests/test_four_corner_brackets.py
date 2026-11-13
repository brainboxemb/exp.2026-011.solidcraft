"""Qualification tests for four HUB75-style outside corner brackets."""
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
]


class FourCornerBracketsCommandTests(unittest.TestCase):
    def test_generated_four_corner_relationship_contract(self):
        document = run_script(
            ROOT / "examples/four-corner-brackets/scpf/model.py"
        )
        commands = document["commands"]

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
            self.assertEqual(joint["angle"], 0.0)
            self.assertEqual(joint["a"]["occurrence"], "FrameBlock:1")
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(joint["b"]["occurrence"], f"LBracket:{index}")
            self.assertEqual(joint["b"]["z"], [0.0, -1.0, 0.0])
            self.assertEqual(joint["b"]["x"], [1.0, 0.0, 0.0])


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class FourCornerBracketsNativeTests(unittest.TestCase):
    def test_native_brackets_match_front_corners(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "four-corner-brackets"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 5)

        brackets = [
            body for body in data["bodies"]
            if body["name"].startswith("LBracket")
        ]
        self.assertEqual(len(brackets), 4)
        self.assertEqual(
            _boxes(brackets),
            sorted([
                ((-60.0, -44.0, 32.0), (-32.0, -40.0, 60.0)),
                ((32.0, -44.0, 32.0), (60.0, -40.0, 60.0)),
                ((32.0, -44.0, 0.0), (60.0, -40.0, 28.0)),
                ((-60.0, -44.0, 0.0), (-32.0, -40.0, 28.0)),
            ]),
        )

    def test_saved_size_mutation_moves_all_four_brackets(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "four-corner-brackets"
            / "measurements-size-160x120x90.json"
        )
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
        self.assertEqual(
            _boxes(brackets),
            sorted([
                ((-80.0, -64.0, 62.0), (-52.0, -60.0, 90.0)),
                ((52.0, -64.0, 62.0), (80.0, -60.0, 90.0)),
                ((52.0, -64.0, 0.0), (80.0, -60.0, 28.0)),
                ((-80.0, -64.0, 0.0), (-52.0, -60.0, 28.0)),
            ]),
        )


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _params(measurements):
    return {row["name"]: row["value"] for row in measurements["params"]}


def _boxes(bodies):
    return sorted(
        (
            tuple(round(v, 6) for v in body["bbox"]["min"]),
            tuple(round(v, 6) for v in body["bbox"]["max"]),
        )
        for body in bodies
    )


if __name__ == "__main__":
    unittest.main()
