"""Regression checks for the standalone CornerBracket example."""
from pathlib import Path
import unittest

from scpf.runner import run_script

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "corner-bracket" / "scpf"


class CornerBracketTests(unittest.TestCase):
    def test_default_is_fast_four_countersinks(self):
        commands = run_script(EXAMPLE / "model.py")["commands"]
        holes = [c for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 4)
        self.assertTrue(all(c["params"].get("type") == "countersink" for c in holes))
        self.assertEqual(len([c for c in commands if c["command"] == "solid.chamfer"]), 2)
        self.assertEqual(len([c for c in commands if c["command"] == "solid.fillet"]), 1)
        # 19 params + 4 sketch+extrude + 3 edge modifiers + 4 holes.
        self.assertEqual(len(commands), 29)

    def test_polygon_segments_have_meaningful_sketch_ids(self):
        commands = run_script(EXAMPLE / "model.py")["commands"]
        sketch = next(c for c in commands if c["command"] == "sketch.line")
        self.assertEqual(
            sketch["params"]["ids"],
            [
                "tip_horizontal_relief", "outer_horizontal_end",
                "outer_horizontal_end_bevel", "outer_horizontal_face",
                "outer_corner_bevel", "outer_vertical_face",
                "outer_vertical_end_bevel", "outer_vertical_end",
                "tip_vertical_relief", "inside_vertical", "inside_horizontal",
            ],
        )

    def test_polygon_segment_ids_are_checked(self):
        from scpf.core import Polygon2D
        points = [(0, 0), (10, 0), (10, 10)]
        for tags in (["a", "b"], ["a", "a", "c"], ["a", "bad id", "c"]):
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                Polygon2D(points, ids=tags)

    def test_outer_chamfer_picks_match_original_geometry(self):
        """Refactoring edge selection must not change the native CAD shape."""
        commands = run_script(EXAMPLE / "model.py")["commands"]
        chamfers = [c for c in commands if c["command"] == "solid.chamfer"]
        outer_edges = chamfers[0]["params"]["edges"]

        expected_xz = [
            (60, 4.8), (58.5, 10.5), (25.5, 12),
            (-9, 9), (-12, -25.5), (-10.5, -58.5),
            (-4.8, -60),
        ]
        self.assertEqual(len(outer_edges), 14)
        for side_index, side in enumerate((-12, 12)):
            for (expected_x, expected_z), point in zip(
                expected_xz, outer_edges[side_index * 7:(side_index + 1) * 7]
            ):
                x, y, z = point
                self.assertAlmostEqual(x, expected_x)
                self.assertAlmostEqual(y, side)
                self.assertAlmostEqual(z, expected_z)

    def test_missing_profile_edge_name_is_rejected(self):
        from scpf.core import Polygon2D, Direction, Edges
        from scpf.features import compile_features
        from scpf.compiler import ModelError

        shape = Polygon2D(
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            plane="XZ",
            ids=["bottom", "right", "top", "left"],
        ).extrude(10, direction=Direction.SYMMETRIC)
        shape = shape.chamfer(1, edges=Edges.from_profile("outer_*"))
        with self.assertRaisesRegex(ModelError, "no polygon segment matches"):
            compile_features(shape, "Square")

    def test_named_profile_selection_requires_segment_ids(self):
        from scpf.core import Polygon2D, Direction, Edges
        from scpf.features import compile_features
        from scpf.compiler import ModelError

        shape = Polygon2D(
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            plane="XZ",
        ).extrude(10, direction=Direction.SYMMETRIC)
        shape = shape.chamfer(1, edges=Edges.from_profile("outer_*"))
        with self.assertRaisesRegex(ModelError, "must define ids"):
            compile_features(shape, "Square")

    def test_original_reference_kept_separate(self):
        commands = run_script(EXAMPLE / "model_reference.py")["commands"]
        holes = [c for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 16)
        self.assertEqual(len(commands), 42)


if __name__ == "__main__":
    unittest.main()
