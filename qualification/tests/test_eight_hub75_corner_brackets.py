"""Qualification contract for eight real HUB75 CornerBracket occurrences."""
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


class EightHub75CornerBracketsCommandTests(unittest.TestCase):
    def test_generated_relationship_contract(self):
        commands = run_script(
            ROOT / "examples/eight-hub75-corner-brackets/scpf/model.py"
        )["commands"]
        components = [
            row["params"]["name"] for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["FrameBlock", "Hub75CornerBracket"])
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
            self.assertEqual(joint["offset"], -12.0)
            self.assertEqual(joint["a"]["corner"], corner)
            self.assertEqual(
                joint["b"]["occurrence"],
                f"Hub75CornerBracket:{index}",
            )

        self.assertTrue(all(j["b"]["z"] == [0.0, 1.0, 0.0] for j in joints[:4]))
        self.assertTrue(all(j["b"]["x"] == [0.0, 0.0, -1.0] for j in joints[:4]))
        self.assertTrue(all(j["b"]["z"] == [0.0, -1.0, 0.0] for j in joints[4:]))
        self.assertTrue(all(j["b"]["x"] == [1.0, 0.0, 0.0] for j in joints[4:]))


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class EightHub75CornerBracketsNativeTests(unittest.TestCase):
    def test_native_body_count(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-hub75-corner-brackets"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 9)

    def test_saved_size_mutation_retains_eight_brackets(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "eight-hub75-corner-brackets"
            / "measurements-size-160x120x90.json"
        )
        self.assertEqual(data["body_count"], 9)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
