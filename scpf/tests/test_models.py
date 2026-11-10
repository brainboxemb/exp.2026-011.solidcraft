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
        generated = run_script(ROOT / "examples/plate/scpf/model.py")
        expected = json.loads((ROOT / "examples/plate/scpf/reference.json").read_text())
        self.assertEqual(generated, expected)
        commands = generated["commands"]
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
        self.assertTrue(all("references" not in c for c in holes))
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

    def test_sample_plate_preserves_original_sketch_and_feature_names(self):
        commands = run_script(ROOT / "examples/sample-plate/scpf/model.py")["commands"]
        self.assertEqual(
            [c["params"]["name"] for c in commands if c["command"] == "sketch.create"],
            ["Base", "Holes", "Boss", "Bore"],
        )
        self.assertEqual(
            [c["command"] for c in commands
             if c["command"] in ("solid.hole", "solid.cylinder")],
            [],
        )
        self.assertEqual(
            [c["params"]["operation"] for c in commands
             if c["command"] == "solid.extrude" and "operation" in c["params"]],
            ["cut", "join", "cut"],
        )
        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "solid.extrude" and "operation" in c["params"]],
            ["Holes", "Boss", "Bore"],
        )
        self.assertEqual(
            [c["params"]["center"] for c in commands
             if c["command"] == "sketch.circle.center"],
            [[12, 25], [68, 25], [40, 25], [40, 25]],
        )
        self.assertEqual(
            [c["params"]["offset"] for c in commands
             if c["command"] == "sketch.create" and "offset" in c["params"]],
            ["thickness", "thickness + 14 mm"],
        )

    def test_sample_plate_parameter_override_preserves_sketch_centres(self):
        with tempfile.TemporaryDirectory() as directory:
            source = (ROOT / "examples/sample-plate/scpf/model.py").read_text()
            script = Path(directory) / "model.py"
            script.write_text(source.replace(
                "SamplePlate()", "SamplePlate(width=100, depth=60, thickness=10)"))
            commands = run_script(script)["commands"]
        self.assertEqual([c["params"]["expression"] for c in commands[:3]],
                         ["100", "60", "10"])
        self.assertEqual(
            [c["params"]["center"] for c in commands
             if c["command"] == "sketch.circle.center"],
            [[12, 30], [88, 30], [50, 30], [50, 30]],
        )
        self.assertFalse(any(c["command"] == "solid.hole" for c in commands))

    def test_anchored_holes_example_compiles_to_one_holes_sketch(self):
        commands = run_script(
            ROOT / "examples/anchored-holes/scpf/model.py")["commands"]
        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "sketch.create"],
            ["Base", "Holes"],
        )
        self.assertEqual(
            [c["params"]["center"] for c in commands
             if c["command"] == "sketch.circle.center"],
            [[50, 10], [50, 50]],
        )
        self.assertFalse(any(c["command"] == "solid.hole" for c in commands))
        self.assertEqual(commands[-1]["command"], "solid.extrude")
        self.assertEqual(commands[-1]["params"]["operation"], "cut")

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

    def test_attached_hole_pattern_builds_one_sketch_cut(self):
        from scpf.core import Anchor, Axis, Depth, Hole, Rectangle2D, Parameter
        from scpf.compiler import compile_model
        width = Parameter("width", 100)
        depth = Parameter("depth", 60)
        thickness = Parameter("thickness", 10)
        plate = Rectangle2D(width, depth).extrude(thickness)
        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=40, axis=Axis.Y
        ).attach(plate, parent=Anchor.TOP)
        commands = compile_model(plate + holes, "Plate")["commands"]

        sketches = [c["params"]["name"] for c in commands
                    if c["command"] == "sketch.create"]
        self.assertEqual(sketches, ["Base", "Holes"])
        circles = [c["params"] for c in commands
                   if c["command"] == "sketch.circle.center"]
        self.assertEqual([c["center"] for c in circles], [[50, 10], [50, 50]])
        self.assertTrue(all(c["diameter"] == 8 for c in circles))
        self.assertFalse(any(c["command"] == "solid.hole" for c in commands))
        self.assertEqual(commands[-1]["command"], "solid.extrude")
        self.assertEqual(commands[-1]["params"]["operation"], "cut")
        self.assertEqual(commands[-1]["params"]["direction"], "positive")
        self.assertEqual(commands[-1]["params"]["distance"], "thickness")

    def test_hole_attach_starts_at_exterior_top(self):
        from scpf.core import Hole, Anchor, Rectangle2D
        from scpf.compiler import compile_model, ModelError
        plate = Rectangle2D(80, 50).extrude(8)
        attached = Hole(d=8).attach(plate, parent=Anchor.TOP)
        commands = compile_model(plate + attached, "Plate")["commands"]
        self.assertEqual(commands[-1]["command"], "solid.extrude")
        self.assertEqual(commands[-1]["params"]["operation"], "cut")
        with self.assertRaises(ModelError):
            compile_model(
                plate - Hole(d=8).attach(plate, parent=Anchor.CENTER),
                "Plate",
            )
        with self.assertRaises(ValueError):
            Hole(d=-2)

    def test_symmetric_anchored_cylinder_pattern_follows_plate_dimensions(self):
        from scpf.core import Anchor, Axis, Cylinder, Rectangle2D
        from scpf.compiler import compile_model
        base = Rectangle2D(100, 60).extrude(10)
        holes = Cylinder(d=8, h=12).pattern(
            count=2, spacing=40, axis=Axis.Y
        ).attach(base, parent=Anchor.CENTER, child=Anchor.CENTER)
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
            Sphere(8).attach(base, parent=Anchor.TOP)
        with self.assertRaises(ValueError):
            Cylinder(d=8, h=10).pattern(count=2, spacing=40, axis=Axis.Z)
        with self.assertRaises(ValueError):
            Cylinder(d=8, h=10).attach(base, offset=(1, 2, 3))

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

    def test_plain_model_class_fields_become_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "class Cuboid:\n"
                "    length = 80.0\n"
                "    width = 50.0\n"
                "    height = 30.0\n"
                "    def build(self):\n"
                "        Box(self.length, self.width, self.height)\n"
                "Cuboid(width=60.0)\n"
            )
            generated = run_script(file)
        self.assertEqual(
            [c["params"]["name"] for c in generated["commands"][:3]],
            ["length", "width", "height"],
        )
        self.assertEqual(
            [c["params"]["expression"] for c in generated["commands"][:3]],
            ["80", "60", "30"],
        )

    def test_plain_model_class_accepts_positional_overrides_in_field_order(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "class Cuboid:\n"
                "    length = 80.0\n"
                "    width = 50.0\n"
                "    height = 30.0\n"
                "    def build(self):\n"
                "        Box(self.length, self.width, self.height)\n"
                "Cuboid(100.0, 70.0)\n"
            )
            generated = run_script(file)
        self.assertEqual(
            [c["params"]["expression"] for c in generated["commands"][:3]],
            ["100", "70", "30"],
        )

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

    def test_pattern_requires_explicit_axes_and_valid_count(self):
        from scpf.core import Axis, Cylinder, Hole
        with self.assertRaises(TypeError):
            Hole(d=8).pattern(x=70, y=30)
        with self.assertRaises(ValueError):
            Cylinder(d=8, h=3).pattern(count=0, spacing=40, axis=Axis.X)
        with self.assertRaises(ValueError):
            Hole(d=8).pattern(count=2, spacing=40, axis=Axis.Z)

    def test_attached_hole_uses_sketch_while_explicit_at_can_be_native(self):
        from scpf.compiler import compile_model
        from scpf.core import Box, Rectangle2D, Polygon2D, Direction, Hole, Anchor
        box = Box(80, 50, 8)
        rectangle = Rectangle2D(80, 50).extrude(8)
        for model in (
            box + Hole(d=6).attach(box, parent=Anchor.TOP),
            rectangle + Hole(d=6).attach(rectangle, parent=Anchor.TOP),
        ):
            commands = compile_model(model, "Widget")["commands"]
            self.assertEqual(commands[-1]["command"], "solid.extrude")
            self.assertEqual(commands[-1]["params"]["operation"], "cut")
            self.assertFalse(any(c["command"] == "solid.hole" for c in commands))

        polygon = Polygon2D(
            [(0, 0), (40, 0), (40, 6), (0, 6)], plane="XZ"
        ).extrude(50, direction=Direction.NEGATIVE)
        commands = compile_model(
            polygon + Hole(d=6).at(20, -25, 0), "Widget"
        )["commands"]
        self.assertEqual(commands[-1]["command"], "solid.hole")

    def test_shell_uses_faces_without_reusing_anchor_semantics(self):
        from scpf.compiler import compile_model
        from scpf.core import Box, Faces
        commands = compile_model(
            Box(80, 50, 30).shell(2, open=Faces.TOP),
            "Enclosure",
        )["commands"]
        self.assertEqual(
            [c["command"] for c in commands],
            [
                "sketch.create",
                "sketch.rectangle.two_point",
                "sketch.finish",
                "solid.extrude",
                "solid.shell",
            ],
        )
        self.assertEqual(commands[0]["params"]["name"], "Enclosure footprint")
        self.assertEqual(commands[4]["params"]["faces"], [[0, 0, 30]])
        self.assertEqual(commands[4]["params"]["thickness"], 2)
        with self.assertRaises(ValueError):
            Box(80, 50, 30).shell(2, open=Faces.TOP).move(x=10)

    def test_bound_relative_offsets_resolve_against_parent_extents(self):
        from scpf.compiler import compile_model
        from scpf.core import Anchor, Boss, Box, Faces, X, Y
        body = Box(80, 50, 30).shell(2, open=Faces.TOP)

        minimum = Boss(d=7, h=12, hole_d=2.5).attach(
            body,
            parent=Anchor.INNER_BOTTOM,
            offset=(X.MIN + 10, Y.MIN + 10),
        )
        body = body + minimum

        maximum = Boss(d=7, h=12, hole_d=2.5).attach(
            body,
            parent=Anchor.INNER_BOTTOM,
            offset=(X.MAX - 10, Y.MAX - 10),
        )
        body = body + maximum

        commands = compile_model(body, "Enclosure")["commands"]
        bosses = [c for c in commands if c["command"] == "plastic.boss"]
        self.assertEqual(
            [boss["params"]["position"] for boss in bosses],
            [[-30, -15, 2], [30, 15, 2]],
        )

    def test_bound_relative_offsets_reject_wrong_axis(self):
        from scpf.core import Anchor, Boss, Box, Faces, X, Y
        body = Box(80, 50, 30).shell(2, open=Faces.TOP)
        with self.assertRaisesRegex(ValueError, "requires X bounds"):
            Boss(d=7, h=12, hole_d=2.5).attach(
                body,
                parent=Anchor.INNER_BOTTOM,
                offset=(Y.MIN + 10, Y.MIN + 10),
            )
        with self.assertRaisesRegex(ValueError, "requires Y bounds"):
            Boss(d=7, h=12, hole_d=2.5).attach(
                body,
                parent=Anchor.INNER_BOTTOM,
                offset=(X.MIN + 10, X.MIN + 10),
            )

    def test_inner_bottom_anchor_requires_shell(self):
        from scpf.compiler import compile_model, ModelError
        from scpf.core import Anchor, Boss, Box
        body = Box(80, 50, 30)
        boss = Boss(d=7, h=12, hole_d=2.5).attach(
            body,
            parent=Anchor.INNER_BOTTOM,
        )
        with self.assertRaises(ModelError):
            compile_model(body + boss, "Enclosure")

    def test_plastic_enclosure_compiles_to_sketch_base_and_native_plastic_features(self):
        commands = run_script(
            ROOT / "examples/plastic-enclosure/scpf/model.py"
        )["commands"]
        feature_commands = [c for c in commands
                            if c["command"] != "parameters.add"]
        self.assertEqual(
            [c["command"] for c in feature_commands],
            [
                "sketch.create",
                "sketch.rectangle.two_point",
                "sketch.finish",
                "solid.extrude",
                "solid.shell",
                "plastic.lip",
                "plastic.snap_fit",
                "plastic.boss",
                "plastic.boss",
                "plastic.rest",
            ],
        )
        self.assertEqual(feature_commands[0]["params"]["name"], "Enclosure footprint")
        self.assertEqual(feature_commands[3]["params"]["body_name"], "Enclosure")
        self.assertTrue(all(
            c["params"].get("body") == "Enclosure"
            for c in feature_commands[4:]
        ))
        self.assertEqual(feature_commands[4]["params"]["faces"], [[0, 0, 30]])
        self.assertEqual(feature_commands[5]["params"]["face"], [-39, 0, 30])
        self.assertEqual(feature_commands[6]["params"]["position"], [0, 19, 2])
        self.assertEqual(feature_commands[6]["params"]["hook"], [0, -1, 0])
        self.assertEqual(
            [feature_commands[7]["params"]["position"],
             feature_commands[8]["params"]["position"]],
            [[-30, -15, 2], [30, 15, 2]],
        )
        self.assertEqual(feature_commands[9]["params"]["position"], [0, 0, 2])
        self.assertEqual(feature_commands[9]["params"]["length"], 24)

    def test_plastic_enclosure_pi_video_feature_sequence(self):
        commands = run_script(
            ROOT / "examples/plastic-enclosure-pi/scpf/model.py"
        )["commands"]
        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "parameters.add"],
            ["board_w", "board_d", "height", "wall"],
        )
        features = [c for c in commands if c["command"] != "parameters.add"]
        self.assertEqual(
            [c["command"] for c in features],
            ["sketch.create", "sketch.rectangle.two_point", "sketch.finish",
             "solid.extrude", "solid.fillet", "solid.shell", "solid.fillet",
             "plastic.boss", "plastic.boss", "plastic.boss", "plastic.boss",
             "sketch.create", "sketch.rectangle.two_point",
             "sketch.rectangle.two_point", "sketch.rectangle.two_point",
             "sketch.finish", "solid.extrude",
             "sketch.create", "sketch.rectangle.two_point",
             "sketch.finish", "solid.extrude",
             "sketch.create", "sketch.rectangle.two_point",
             "sketch.rectangle.two_point", "sketch.rectangle.two_point",
             "sketch.rectangle.two_point", "sketch.rectangle.two_point",
             "sketch.finish", "solid.extrude",
             "sketch.create", "sketch.text", "sketch.finish", "solid.extrude",
             "material.create", "material.assign"],
        )
        self.assertIn("board_w", str(features[1]["params"]["p0"][0]))
        self.assertIn("board_d", str(features[1]["params"]["p1"][1]))
        self.assertEqual(features[4]["params"]["radius"], 5.0)
        self.assertEqual(features[6]["params"]["radius"], 1.0)
        bosses = [c["params"] for c in features if c["command"] == "plastic.boss"]
        self.assertEqual(
            [p["position"] for p in bosses],
            [[-39, -24.5, 2], [19, -24.5, 2],
             [-39, 24.5, 2], [19, 24.5, 2]],
        )
        self.assertTrue(all(p["hole_diameter"] == 2.5 for p in bosses))
        self.assertEqual(
            [c["params"]["name"] for c in features
             if c["command"] == "sketch.create"],
            ["PlasticEnclosurePi footprint", "Pi ports",
             "USB and Ethernet", "Floor vents", "Pi 4 engraving"],
        )
        cuts = [c for c in features if c["command"] == "solid.extrude"
                and c["params"].get("operation") == "cut"]
        self.assertEqual(len(cuts), 4)
        self.assertEqual([c["params"]["direction"] for c in cuts],
                         ["negative", "negative", "negative", "negative"])
        self.assertEqual(
            [c["command"] for c in features[-6:]],
            ["sketch.create", "sketch.text", "sketch.finish", "solid.extrude",
             "material.create", "material.assign"],
        )
        self.assertEqual(features[-5]["params"]["text"], "Pi 4")
        self.assertEqual(features[-2]["params"]["density_g_cm3"], 1.27)
        self.assertEqual(features[-1]["params"]["material"], "PETG")

    def test_history_policy_can_lower_boss_to_sketches(self):
        commands = run_script(
            ROOT / "examples/history-policy/scpf/model.py"
        )["commands"]
        feature_commands = [
            c for c in commands if c["command"] != "parameters.add"
        ]
        self.assertEqual(
            [c["command"] for c in feature_commands],
            [
                "sketch.create",
                "sketch.rectangle.two_point",
                "sketch.finish",
                "solid.extrude",
                "plastic.boss",
                "sketch.create",
                "sketch.circle.center",
                "sketch.finish",
                "solid.extrude",
                "sketch.create",
                "sketch.circle.center",
                "sketch.finish",
                "solid.extrude",
                "sketch.create",
                "sketch.circle.center",
                "sketch.finish",
                "solid.extrude",
            ],
        )
        self.assertEqual(
            [c["params"].get("name") for c in feature_commands
             if c["command"] == "sketch.create"],
            [
                "HistoryPolicyBoss footprint",
                "Boss",
                "Boss hole",
                "Explicit pad",
            ],
        )

    def test_explicit_sketch_scope_requires_profiles_and_closes_before_extrude(self):
        from scpf.core import Box, Circle2D
        from scpf.explicit_sketch import Sketch

        body = Box(40, 30, 6)
        with self.assertRaisesRegex(ValueError, "at least one profile"):
            with Sketch(name="Empty", on=body):
                pass

        sketch = Sketch(name="Pad", on=body)
        with sketch:
            sketch.add(Circle2D(d=10))
            with self.assertRaisesRegex(ValueError, "before extruding"):
                sketch.extrude(5)

        self.assertEqual(sketch.extrude(5).kind, "explicit_sketch_extrusion")

    def test_history_policy_scope_does_not_leak(self):
        from scpf.core import Boss
        from scpf.history import History, behavior

        with behavior(history=History.SKETCH):
            inside = Boss(d=12, h=10)
        outside = Boss(d=12, h=10)

        self.assertIs(inside.history, History.SKETCH)
        self.assertIsNone(outside.history)

    def test_circle_profile_extrudes_without_an_explicit_sketch_object(self):
        from scpf.compiler import compile_model
        from scpf.core import Circle2D
        commands = compile_model(Circle2D(d=12).extrude(8), "Pin")["commands"]
        self.assertEqual([c["command"] for c in commands],
                         ["sketch.create", "sketch.circle.center",
                          "sketch.finish", "solid.extrude"])
        self.assertEqual(commands[1]["params"]["diameter"], 12)

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
