"""Qualification contract for direct negative Circle2D extrusion."""

from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class CircleNegativeExtrudeCommandTests(unittest.TestCase):
    def test_direct_circle_extrude_preserves_negative_direction(self):
        commands = run_script(
            ROOT / "examples/circle-negative-extrude/scpf/model.py"
        )["commands"]

        feature_commands = [
            row for row in commands
            if row["command"] != "parameters.add"
        ]
        self.assertEqual(
            [row["command"] for row in feature_commands],
            [
                "sketch.create",
                "sketch.circle.center",
                "sketch.finish",
                "solid.extrude",
            ],
        )

        circle = feature_commands[1]["params"]
        self.assertEqual(circle["center"], [0, 0])
        self.assertEqual(circle["diameter"], "diameter")

        extrude = feature_commands[3]["params"]
        self.assertEqual(extrude["distance"], "height")
        self.assertEqual(extrude["direction"], "negative")


if __name__ == "__main__":
    unittest.main()
