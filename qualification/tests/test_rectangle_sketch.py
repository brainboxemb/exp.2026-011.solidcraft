"""Qualification contract for explicit Rectangle2D sketches."""

from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class RectangleSketchCommandTests(unittest.TestCase):
    def test_named_sketch_uses_native_rectangle(self):
        commands = run_script(
            ROOT / "examples/rectangle-sketch/scpf/model.py"
        )["commands"]

        rectangles = [
            row["params"]
            for row in commands
            if row["command"] == "sketch.rectangle.two_point"
            and row["params"].get("p0") == [
                "((-(base_width)) / 2) + (base_width / 2) + (-20 mm)",
                "((-(base_depth)) / 2) + (base_depth / 2) + (-15 mm)",
            ]
            and row["params"].get("p1") == [
                "((-(base_width)) / 2) + (base_width / 2) + (-20 mm) + (pad_width)",
                "((-(base_depth)) / 2) + (base_depth / 2) + (-15 mm) + (pad_depth)",
            ]
        ]
        self.assertEqual(len(rectangles), 1)

        sketches = [
            row["params"].get("name")
            for row in commands
            if row["command"] == "sketch.create"
        ]
        self.assertIn("Rectangle pad", sketches)

        extrude = next(
            row["params"]
            for row in commands
            if row["command"] == "solid.extrude"
            and row["params"].get("name") == "Rectangle pad"
        )
        self.assertEqual(extrude["distance"], "pad_height")
        self.assertEqual(extrude["direction"], "positive")
        self.assertEqual(extrude["operation"], "join")


if __name__ == "__main__":
    unittest.main()
