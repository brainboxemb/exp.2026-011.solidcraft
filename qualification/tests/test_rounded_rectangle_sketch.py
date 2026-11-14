"""Qualification contract for explicit RoundedRectangle2D sketches."""

from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class RoundedRectangleSketchCommandTests(unittest.TestCase):
    def test_named_sketch_uses_native_rounded_rectangle(self):
        commands = run_script(
            ROOT / "examples/rounded-rectangle-sketch/scpf/model.py"
        )["commands"]

        rounded = [
            row["params"]
            for row in commands
            if row["command"] == "sketch.rectangle.rounded"
        ]
        self.assertEqual(len(rounded), 1)
        self.assertEqual(rounded[0]["radius"], "radius")

        sketches = [
            row["params"].get("name")
            for row in commands
            if row["command"] == "sketch.create"
        ]
        self.assertIn("Rounded pad", sketches)

        extrude = next(
            row["params"]
            for row in commands
            if row["command"] == "solid.extrude"
            and row["params"].get("name") == "Rounded pad"
        )
        self.assertEqual(extrude["distance"], "pad_height")
        self.assertEqual(extrude["direction"], "positive")
        self.assertEqual(extrude["operation"], "join")


if __name__ == "__main__":
    unittest.main()
