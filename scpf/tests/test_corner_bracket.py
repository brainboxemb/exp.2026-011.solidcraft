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
        self.assertEqual(len([c for c in commands if c["command"] == "solid.chamfer"]), 3)
        self.assertEqual(len([c for c in commands if c["command"] == "solid.fillet"]), 1)
        # 18 params + 4 sketch/extrude + 4 edge modifiers + 4 holes.
        self.assertEqual(len(commands), 30)

    def test_named_polygon_vertices_generate_sketch_ids(self):
        from scpf.core import Polygon2D
        profile = Polygon2D([
            ("bottom", (0, 0)), ("right", (10, 0)),
            ("top", (10, 8)), ("left", (0, 8)),
        ], plane="XZ", world=True)
        points, plane, ids = profile.data
        self.assertEqual(plane, "XZ")
        self.assertEqual(points, ((0, 0), (10, 0), (10, -8), (0, -8)))
        self.assertEqual(ids, ("bottom", "right", "top", "left"))

        with self.assertRaisesRegex(ValueError, "all polygon vertices"):
            Polygon2D([("a", (0, 0)), (10, 0), (10, 10)])
        with self.assertRaisesRegex(ValueError, "cannot also specify ids"):
            Polygon2D([("a", (0, 0)), ("b", (10, 0)), ("c", (0, 10))],
                      ids=["a", "b", "c"])

    def test_polygon_segments_have_meaningful_sketch_ids(self):
        commands = run_script(EXAMPLE / "model.py")["commands"]
        sketch = next(c for c in commands if c["command"] == "sketch.line")
        self.assertEqual(
            sketch["params"]["ids"],
            [
                "i_corner", "o_hor_tip", "o_hor_bevel",
                "o_hor", "o_corner",
                "o_vert", "o_vert_bevel",
                "o_vert_end", "v_tip",
            ],
        )

    def test_polygon_segment_ids_are_checked(self):
        from scpf.core import Polygon2D
        points = [(0, 0), (10, 0), (10, 10)]
        for tags in (["a", "b"], ["a", "a", "c"], ["a", "bad id", "c"]):
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                Polygon2D(points, ids=tags)

    def test_named_edges_and_tip_relief_compile_to_separate_features(self):
        """Sketch contains no EF cuts; native chamfer adds them explicitly."""
        commands = run_script(EXAMPLE / "model.py")["commands"]
        sketch = next(c for c in commands if c["command"] == "sketch.line")
        self.assertEqual(len(sketch["params"]["points"]), 9)

        fillet = next(c for c in commands if c["command"] == "solid.fillet")
        self.assertEqual(fillet["params"]["edges"], [[0, 0, 0]])

        chamfers = [c["params"] for c in commands if c["command"] == "solid.chamfer"]
        self.assertEqual(chamfers[0]["edges"], [[60, 0, 0], [0, 0, -60]])
        self.assertEqual(chamfers[0]["distance"], "elephant_foot_relief")

        expected_xz = [
            (60, 4.5), (58.5, 10.5), (25.5, 12),
            (-9, 9), (-12, -25.5), (-10.5, -58.5),
            (-4.5, -60),
        ]
        self.assertEqual(len(chamfers[1]["edges"]), 14)
        for side_index, side in enumerate((-12, 12)):
            for (expected_x, expected_z), point in zip(
                expected_xz, chamfers[1]["edges"][side_index * 7:(side_index + 1) * 7]
            ):
                x, y, z = point
                self.assertAlmostEqual(x, expected_x)
                self.assertAlmostEqual(y, side)
                self.assertAlmostEqual(z, expected_z)

        self.assertEqual(chamfers[2]["edges"], [[30, -12, 0], [30, 12, 0]])
        self.assertEqual(chamfers[2]["distance"], "elephant_foot_relief")

    def test_missing_profile_edge_name_is_rejected(self):
        from scpf.core import Polygon2D, Direction, Edges
        from scpf.features import compile_features
        from scpf.compiler import ModelError

        shape = Polygon2D(
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            plane="XZ",
            ids=["bottom", "right", "top", "left"],
        ).extrude(10, direction=Direction.SYMMETRIC)
        shape = shape.chamfer(1, edges=Edges.from_profile("o_*"))
        with self.assertRaisesRegex(ModelError, "no polygon segment or vertex matches"):
            compile_features(shape, "Square")

    def test_named_profile_selection_requires_segment_ids(self):
        from scpf.core import Polygon2D, Direction, Edges
        from scpf.features import compile_features
        from scpf.compiler import ModelError

        shape = Polygon2D(
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            plane="XZ",
        ).extrude(10, direction=Direction.SYMMETRIC)
        shape = shape.chamfer(1, edges=Edges.from_profile("o_*"))
        with self.assertRaisesRegex(ModelError, "must define ids"):
            compile_features(shape, "Square")

    def test_sweep_edge_selection_uses_named_vertices(self):
        from scpf.core import Polygon2D, Direction, Edges
        from scpf.features import compile_features

        shape = Polygon2D([
            ("start", (0, 0)), ("tip", (10, 0)),
            ("far", (10, 8)), ("end", (0, 8)),
        ], plane="XZ", world=True).extrude(8, direction=Direction.SYMMETRIC)
        shape = shape.chamfer(0.5, edges=Edges.from_vertices("tip", "end"))
        chamfer = next(
            c for c in compile_features(shape, "Plate")
            if c["command"] == "solid.chamfer"
        )
        self.assertEqual(chamfer["params"]["edges"], [[10, 0, 0], [0, 0, 8]])

    def test_original_reference_kept_separate(self):
        commands = run_script(EXAMPLE / "model_reference.py")["commands"]
        holes = [c for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 16)
        self.assertEqual(len(commands), 42)


if __name__ == "__main__":
    unittest.main()
