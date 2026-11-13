"""Qualification contract for eight asymmetric 3D flightcase corners."""
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


class EightFlightcaseCornersCommandTests(unittest.TestCase):
    def test_all_eight_3d_corners_reuse_one_component(self):
        commands = run_script(
            ROOT / "examples/eight-flightcase-corners/scpf/model.py"
        )["commands"]
        components = [
            row["params"]["name"] for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["CaseBlock", "FlightcaseCorner"])
        self.assertEqual(
            len([row for row in commands if row["command"] == "occurrence.copy"]),
            7,
        )

        joints = [
            row["params"] for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 8)
        for index, (joint, corner) in enumerate(zip(joints, EXPECTED_CORNERS), 1):
            self.assertEqual(joint["type"], "rigid")
            self.assertEqual(joint["angle"], 0.0)
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(
                joint["b"]["occurrence"],
                f"FlightcaseCorner:{index}",
            )
            self.assertEqual(joint["b"]["z"], [0.0, -1.0, 0.0])
            self.assertEqual(joint["b"]["x"], [1.0, 0.0, 0.0])


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class EightFlightcaseCornersNativeTests(unittest.TestCase):
    def test_native_body_count(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-flightcase-corners"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 9)

    def test_saved_size_mutation_retains_eight_corners(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-flightcase-corners"
            / "measurements-size-160x120x90.json"
        )
        self.assertEqual(data["body_count"], 9)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
