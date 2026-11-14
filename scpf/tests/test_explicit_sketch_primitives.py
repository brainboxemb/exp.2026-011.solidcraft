"""Regression contract: native primitives and explicit standalone sketches."""
import unittest

from scpf import Box, Rectangle2D, Circle2D, Sketch, Parameter
from scpf.compiler import compile_model


class NativePrimitiveTests(unittest.TestCase):
    def test_box_requires_no_implicit_sketch(self):
        commands = compile_model(
            Box(Parameter("length", 40), Parameter("width", 30),
                Parameter("height", 10)), "BoxModel"
        )["commands"]
        self.assertEqual(
            [c["command"] for c in commands],
            ["parameters.add", "parameters.add", "parameters.add", "solid.box"],
        )
        box = commands[-1]["params"]
        self.assertEqual(box["body_name"], "BoxModel")
        self.assertEqual(box["length"], "length")
        self.assertEqual(box["width"], "width")
        self.assertEqual(box["height"], "height")
        self.assertEqual(box["corner"], ["-length / 2", "-width / 2", 0])

    def test_2d_profile_has_no_direct_extrude_api(self):
        profile = Rectangle2D(40, 30)
        self.assertFalse(hasattr(profile, "extrude"))

    def test_rectangle_in_with_sketch_is_explicit(self):
        with Sketch(plane="XY") as sketch:
            Rectangle2D(40, 30)
        commands = compile_model(sketch.extrude(10), "Plate")["commands"]
        self.assertEqual(
            [c["command"] for c in commands],
            ["sketch.create", "sketch.rectangle.two_point",
             "sketch.finish", "solid.extrude"],
        )
        self.assertEqual(commands[1]["params"]["p1"], [40, 30])
        self.assertEqual(commands[-1]["params"]["body_name"], "Plate")

    def test_circle_in_with_sketch_negative_extrusion(self):
        with Sketch(plane="XY") as sketch:
            Circle2D(d=20)
        commands = compile_model(
            sketch.extrude(30, direction="negative"), "Cylinder"
        )["commands"]
        self.assertEqual(commands[1]["command"], "sketch.circle.center")
        self.assertEqual(commands[-1]["params"]["direction"], "negative")

    def test_existing_attached_sketch_still_works(self):
        base = Box(80, 60, 5)
        with Sketch(name="Pad", on=base) as sketch:
            sketch.add(Rectangle2D(40, 30), offset=(-20, -15))
        commands = compile_model(base + sketch.extrude(8), "Part")["commands"]
        self.assertEqual(commands[0]["command"], "solid.box")
        self.assertEqual(
            [c["command"] for c in commands].count("sketch.create"), 1
        )

    def test_empty_sketch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one profile"):
            with Sketch(plane="XY"):
                pass


if __name__ == "__main__":
    unittest.main()
