"""Regression tests against reviewed SolidCraft 0.30.1 command fixtures."""
import json
import tempfile
import unittest
from pathlib import Path

from scpf.compiler import ModelError
from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class SCPFExamples(unittest.TestCase):
    def test_csg_cube_matches_reviewed_native_commands(self):
        generated = run_script(ROOT / "examples/csg-cube/scpf/model.py")
        expected = json.loads((ROOT / "examples/csg-cube/scpf/reference.json").read_text())
        self.assertEqual(generated, expected)
        self.assertEqual(generated["commands"][0]["params"]["name"], "size")
        self.assertEqual(generated["commands"][1]["params"]["radius"], "size / 1.5")

    def test_plate_uses_generic_box_and_native_holes(self):
        commands = run_script(ROOT / "examples/plate/scpf/model.py")["commands"]
        self.assertEqual([c["params"]["name"] for c in commands[:3]],
                         ["length", "width", "thickness"])
        self.assertEqual([c["params"]["name"] for c in commands
                          if c["command"] == "sketch.create"], ["Plate footprint"])
        holes = [c["params"] for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 4)
        self.assertEqual([c["position"] for c in holes],
                         [[-35, -15, 10], [35, -15, 10],
                          [35, 15, 10], [-35, 15, 10]])
        self.assertTrue(all(c["diameter"] == 8 for c in holes))
        self.assertTrue(all(c["targets"] == ["Plate"] for c in holes))
        self.assertTrue(all(len(c["references"]) == 2 for c in holes))
        self.assertFalse(any(c["command"] == "solid.cylinder" for c in commands))
        self.assertEqual([c["command"] for c in commands].count("solid.fillet"), 1)

    def test_bracket_matches_corrected_native_commands(self):
        generated = run_script(ROOT / "examples/bracket/scpf/model.py")
        expected = json.loads(
            (ROOT / "examples/bracket/scpf/solidcraft.json").read_text()
        )
        self.assertEqual(generated, expected)

        original = json.loads(
            (ROOT / "examples/bracket/source/bracket.json").read_text()
        )
        # The input source used sketch + cut. SCPF now emits native Hole
        # features for the same two entry points; the base and fillet match.
        self.assertEqual(generated["commands"][2:7], original["commands"][2:7])
        self.assertEqual([c["command"] for c in generated["commands"][7:]],
                         ["solid.hole", "solid.hole"])
        self.assertEqual([c["params"]["position"]
                          for c in generated["commands"][7:]],
                         [[25, -15, 0], [25, -45, 0]])
        self.assertEqual([c["params"]["depth"]
                          for c in generated["commands"][7:]],
                         ["thickness", "thickness"])
        self.assertEqual(generated["commands"][6]["params"]["edges"],
                         [[40, -30, -6]])

    def test_bracket_width_and_thickness_override(self):
        with tempfile.TemporaryDirectory() as directory:
            source = (ROOT / "examples/bracket/scpf/model.py").read_text()
            file = Path(directory) / "model.py"
            file.write_text(source.replace("Bracket()", "Bracket(70, 8)"))
            generated = run_script(file)
        self.assertEqual(generated["commands"][0]["params"]["expression"], "70")
        self.assertEqual(generated["commands"][1]["params"]["expression"], "8")
        self.assertEqual(generated["commands"][3]["params"]["points"][2], [40, 8])
        self.assertEqual(generated["commands"][6]["params"]["edges"], [[40, -35, -8]])

    def test_sample_plate_native_holes_and_boss_history(self):
        """A native Hole feature needs no explicit sketch in the script."""
        commands = run_script(ROOT / "examples/sample-plate/scpf/model.py")["commands"]
        sketches = [c["params"]["name"] for c in commands
                    if c["command"] == "sketch.create"]
        self.assertEqual(sketches, ["Base", "Boss"])
        self.assertEqual([c["command"] for c in commands
                          if c["command"] in ("solid.hole", "solid.cylinder")],
                         ["solid.hole", "solid.hole", "solid.hole"])
        holes = [c["params"] for c in commands if c["command"] == "solid.hole"]
        self.assertEqual([h["diameter"] for h in holes], [8, 8, 12])
        self.assertEqual([h["position"] for h in holes],
                         [[12, 25, 8], [68, 25, 8], [40, 25, 22]])
        self.assertEqual([c["params"]["operation"] for c in commands
                          if c["command"] == "solid.extrude" and
                          "operation" in c["params"]], ["join"])
        self.assertEqual([c["params"]["offset"] for c in commands
                          if c["command"] == "sketch.create" and
                          "offset" in c["params"]], ["thickness"])

    def test_sample_plate_parameter_override_updates_native_holes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = (ROOT / "examples/sample-plate/scpf/model.py").read_text()
            script = Path(directory) / "model.py"
            script.write_text(source.replace(
                "SamplePlate()", "SamplePlate(width=100, depth=60, thickness=10)"))
            commands = run_script(script)["commands"]
        self.assertEqual([c["params"]["expression"] for c in commands[:3]],
                         ["100", "60", "10"])
        holes = [c["params"] for c in commands if c["command"] == "solid.hole"]
        self.assertEqual([h["position"] for h in holes],
                         [[12, 30, 10], [88, 30, 10], [50, 30, 24]])
        self.assertTrue(all("references" in h for h in holes[:2]))
        self.assertNotIn("references", holes[2])
        self.assertFalse(any(c["command"] == "solid.cylinder" for c in commands))

    def test_named_edge_selection_and_explicit_edge_points(self):
        from scpf.core import Box, Edges
        body = Box(80, 50, 8)
        self.assertIs(body.fillet(6).data[2], Edges.VERTICAL)
        self.assertIs(body.fillet(6, edges=Edges.VERTICAL).data[2], Edges.VERTICAL)
        self.assertEqual(body.fillet(6, edges=[(0, 0, 4)]).data[2], [(0, 0, 4)])
        with self.assertRaises(ValueError):
            body.fillet(6, edges="vertical")

    def test_direction_enum_compiles_to_solidcraft_strings(self):
        from scpf.core import Circle2D, Direction
        from scpf.compiler import compile_model
        self.assertEqual(Direction.POSITIVE.value, "positive")
        self.assertEqual(Direction.NEGATIVE.value, "negative")
        shape = Circle2D(d=8).extrude(8, direction=Direction.NEGATIVE)
        self.assertEqual(shape.data[2], "negative")
        self.assertEqual(
            Circle2D(d=8).extrude(8, direction="negative").data[2], "negative"
        )
        self.assertEqual(
            Circle2D(d=8).extrude(8).data[2], "positive"
        )
        with self.assertRaises(ValueError):
            Circle2D(d=8).extrude(8, direction="sideways")

    def test_removed_aliases_are_not_exposed(self):
        import scpf
        for name in ("Rectangle", "Circle", "Polygon", "Cube", "Box3D", "Cylinder3D", "Sphere3D"):
            self.assertFalse(hasattr(scpf, name), name)

    def test_sample_plate_uses_edge_enum(self):
        source = (ROOT / "examples/sample-plate/scpf/model.py").read_text()
        self.assertIn("edges=Edges.VERTICAL", source)
        run_script(ROOT / "examples/sample-plate/scpf/model.py")

    def test_hole_is_a_native_feature_with_edge_references(self):
        from scpf.core import Anchor, Axis, Depth, Hole, Rectangle2D, Parameter
        from scpf.compiler import compile_model
        width = Parameter("width", 100)
        depth = Parameter("depth", 60)
        thickness = Parameter("thickness", 10)
        plate = Rectangle2D(width, depth).extrude(thickness)
        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=40, axis=Axis.Y
        ).on(plate, Anchor.TOP)
        native = compile_model(plate + holes, "Plate")["commands"]
        features = [x["params"] for x in native if x["command"] == "solid.hole"]
        self.assertEqual(len(features), 2)
        self.assertEqual([x["position"] for x in features],
                         [[50, 10, 10], [50, 50, 10]])
        self.assertTrue(all(x["references"][0]["distance"] == "(width / 2)" for x in features))
        self.assertTrue(all("depth" in x["references"][1]["distance"] for x in features))
        self.assertTrue(all("depth" not in x for x in features))

    def test_hole_requires_exterior_face(self):
        from scpf.core import Hole, Anchor, Rectangle2D
        from scpf.compiler import compile_model, ModelError
        plate = Rectangle2D(80, 50).extrude(8)
        commands = compile_model(plate + Hole(d=8).on(plate, Anchor.TOP), "Plate")["commands"]
        self.assertEqual(commands[-1]["command"], "solid.hole")
        legacy = compile_model(plate - Hole(d=8).on(plate, Anchor.TOP), "Plate")["commands"]
        self.assertEqual(legacy[-1]["command"], "solid.hole")
        with self.assertRaises(ModelError):
            compile_model(plate - Hole(d=8).on(plate, Anchor.CENTER), "Plate")
        with self.assertRaises(ValueError):
            Hole(d=-2)

    def test_symmetric_anchored_hole_pattern_follows_plate_dimensions(self):
        from scpf.core import Anchor, Axis, Cylinder, Rectangle2D
        from scpf.compiler import compile_model
        base = Rectangle2D(100, 60).extrude(10)
        holes = Cylinder(d=8, h=12).pattern(
            count=2, spacing=40, axis=Axis.Y
        ).on(base, Anchor.CENTER)
        commands = compile_model(base - holes, "Plate")["commands"]
        cylinders = [c["params"] for c in commands
                     if c["command"] == "solid.cylinder"]
        self.assertEqual(len(cylinders), 2)
        self.assertEqual([c["base"][0] for c in cylinders], [50, 50])
        self.assertEqual([c["base"][1] for c in cylinders], [10, 50])
        self.assertEqual([c["base"][2] for c in cylinders], [-1, -1])
        self.assertEqual([c["operation"] for c in cylinders], ["cut", "cut"])

    def test_attached_boss_tracks_plate_top_and_offsets(self):
        from scpf.core import Anchor, Cylinder, Rectangle2D, Parameter
        from scpf.compiler import compile_model
        width, depth, thickness = (
            Parameter("width", 80), Parameter("depth", 50),
            Parameter("thickness", 8)
        )
        base = Rectangle2D(width, depth).extrude(thickness)
        boss = Cylinder(d=24, h=14).attach(
            base, parent=Anchor.TOP, child=Anchor.BOTTOM)
        commands = compile_model(base + boss, "Plate")["commands"]
        self.assertEqual(commands[-1]["command"], "solid.extrude")
        self.assertEqual(commands[-1]["params"]["operation"], "join")
        sketches = [c["params"] for c in commands if c["command"] == "sketch.create"]
        self.assertEqual(sketches[-1]["name"], "Boss")
        self.assertEqual(sketches[-1]["offset"], "thickness")
        boss_circle = [c["params"] for c in commands
                       if c["command"] == "sketch.circle.center"][-1]
        self.assertEqual(boss_circle["diameter"], 24)
        self.assertEqual(boss_circle["center"], [40, 25])

    def test_relative_anchor_rejects_unsupported_usage(self):
        from scpf.core import Anchor, Axis, Cylinder, Rectangle2D, Sphere
        base = Rectangle2D(80, 50).extrude(8)
        with self.assertRaises(ValueError):
            Sphere(8).on(base, Anchor.TOP)
        with self.assertRaises(ValueError):
            Cylinder(d=8, h=10).pattern(count=2, spacing=40, axis=Axis.Z)
        with self.assertRaises(ValueError):
            Cylinder(d=8, h=10).on(base, offset=(1, 2, 3))

    def test_cylinder_keyword_form_is_direct_3d_primitive(self):
        from scpf.core import Cylinder
        self.assertEqual(Cylinder(d=24, h=14).kind, "cylinder")
        self.assertEqual(Cylinder(d=24, h=14).at(40, 25, 8).kind, "placed3d")

    def test_cylinder_standalone_native_command(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "model.py"
            script.write_text(
                "@dataclass\n"
                "class Pin:\n"
                "    diameter: float = 12\n"
                "    def build(self):\n"
                "        Cylinder(d=self.diameter, h=20).at(10, 5, 3)\n"
                "Pin()\n"
            )
            commands = run_script(script)["commands"]
        cylinder = commands[-1]
        self.assertEqual(cylinder["command"], "solid.cylinder")
        self.assertEqual(cylinder["params"]["base"], [10, 5, 3])
        self.assertEqual(cylinder["params"]["diameter"], "diameter")
        self.assertEqual(cylinder["params"]["operation"], "new")

    def test_frozen_dataclass_build_with_implicit_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "@dataclass(frozen=True)\n"
                "class Cuboid:\n"
                "    size: float = 50\n"
                "    def __post_init__(self):\n"
                "        assert self.size > 0\n"
                "    def build(self):\n"
                "        Box(self.size, self.size, self.size).move(x=10)\n"
                "Cuboid(80)\n"
            )
            generated = run_script(file)
        self.assertEqual(generated["commands"][0]["params"]["name"], "size")
        self.assertEqual(generated["commands"][0]["params"]["expression"], "80")
        self.assertEqual(generated["commands"][1]["params"]["center"], [10, 0, 0])

    def test_dataclass_constructor_validates_before_symbolic_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "@dataclass\n"
                "class Cuboid:\n"
                "    size: float = 50\n"
                "    def __post_init__(self):\n"
                "        assert self.size > 0\n"
                "    def build(self):\n"
                "        Box(self.size, self.size, self.size)\n"
                "Cuboid(-5)\n"
            )
            with self.assertRaises(AssertionError):
                run_script(file)

    def test_dataclass_requires_build_method(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "@dataclass\n"
                "class Cuboid:\n"
                "    size: float = 50\n"
                "Cuboid()\n"
            )
            with self.assertRaisesRegex(TypeError, "must define build"):
                run_script(file)

    def test_dataclass_build_must_finish_with_geometry(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "@dataclass\n"
                "class Cuboid:\n"
                "    size: float = 50\n"
                "    def build(self):\n"
                "        body = Box(self.size, self.size, self.size)\n"
                "Cuboid()\n"
            )
            with self.assertRaisesRegex(TypeError, "finish with a Shape"):
                run_script(file)

    def test_arguments_are_editable_without_decorators(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def CsgCube(size=50.0):\n"
                "    return Sphere(size / 1.5) & Box(size, size, size)\n"
                "CsgCube(60.0)\n"
            )
            generated = run_script(file)
        self.assertEqual(generated["commands"][0]["params"]["expression"], "60")
        self.assertEqual(generated["commands"][1]["params"]["radius"], "size / 1.5")

    def test_invalid_plate_cutter_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def Plate(length=100, width=60, thickness=10):\n"
                "    body = Box(length, width, thickness).fillet(2)\n"
                "    return body - Cylinder(d=8, h=3).pattern(x=70, y=30)\n"
                "Plate()\n"
            )
            with self.assertRaises(ModelError):
                run_script(file)

    def test_move_translates_a_csg_composite_without_changing_sizes(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def CsgCube(size=50.0):\n"
                "    body = Sphere(size / 1.5) & Box(size, size, size)\n"
                "    holes = Cylinder(d=size / 1.5, h=size).orient(X, Y, Z)\n"
                "    return (body - holes).move(x=10, y=20, z=30)\n"
                "CsgCube()\n"
            )
            document = run_script(file)
        commands = document["commands"]
        self.assertEqual(commands[1]["params"]["center"], [10, 20, 30])
        self.assertEqual(commands[2]["params"]["center"], [10, 20, 30])
        self.assertEqual(commands[3]["params"]["base"], ["(-(size) / 2) + 10", 20, 30])
        self.assertEqual(commands[4]["params"]["base"], [10, "(-(size) / 2) + 20", 30])
        self.assertEqual(commands[5]["params"]["base"], [10, 20, "(-(size) / 2) + 30"])

    def test_move_rejects_non_finite_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def Cuboid(size=50):\n"
                "    return Box(size, size, size).move(x=float('nan'))\n"
                "Cuboid()\n"
            )
            with self.assertRaises(ValueError):
                run_script(file)

    def test_model_function_implicit_shape_expression(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def Cuboid(size=50):\n"
                "    body = Box(size, size, size)\n"
                "    body.move(x=10)\n"
                "Cuboid()\n"
            )
            generated = run_script(file)
        self.assertEqual(generated["commands"][1]["params"]["center"], [10, 0, 0])

    def test_assignment_only_function_must_still_explicitly_return(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def Cuboid(size=50):\n"
                "    body = Box(size, size, size)\n"
                "Cuboid()\n"
            )
            with self.assertRaises(TypeError):
                run_script(file)

    def test_script_requires_final_model_expression(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text("def CubeModel(size=50):\n    return Box(size, size, size)\n")
            with self.assertRaises(SyntaxError):
                run_script(file)


if __name__ == "__main__":
    unittest.main()
