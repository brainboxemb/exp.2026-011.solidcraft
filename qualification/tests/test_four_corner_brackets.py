"""Qualification contract for four middle-plane CornerBrackets."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")

EXPECTED_SOURCE_CORNERS = [
    [-160.0, -60.0, 160.0],
    [160.0, -60.0, 160.0],
    [160.0, -60.0, 0.0],
    [-160.0, -60.0, 0.0],
]


class FourCornerBracketsCommandTests(unittest.TestCase):
    def test_shared_polygon_component_uses_middle_depth_gap(self):
        commands = run_script(
            ROOT / "examples/four-corner-brackets/scpf/model.py"
        )["commands"]

        components = [
            row["params"]["name"] for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["FrameBlock", "CornerBracket"])
        self.assertEqual(
            len([row for row in commands if row["command"] == "occurrence.copy"]),
            3,
        )

        joints = [
            row["params"] for row in commands
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 4)
        for index, (joint, corner) in enumerate(
            zip(joints, EXPECTED_SOURCE_CORNERS), 1
        ):
            self.assertEqual(joint["type"], "rigid")
            self.assertEqual(joint["angle"], 0.0)
            self.assertIn("frame_depth", str(joint["offset"]))
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(
                joint["b"]["occurrence"], f"CornerBracket:{index}"
            )


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class FourCornerBracketsNativeTests(unittest.TestCase):
    def test_native_body_count(self):
        data = _load(Path(NATIVE_ROOT) / "four-corner-brackets" / "measurements.json")
        self.assertEqual(data["body_count"], 5)

    def test_saved_size_mutation_retains_four_brackets(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "four-corner-brackets"
            / "measurements-size-400x160x200.json"
        )
        self.assertEqual(data["body_count"], 5)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
