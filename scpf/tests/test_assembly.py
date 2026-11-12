"""Reusable model objects and native SolidCraft assembly command tests."""
from pathlib import Path
import tempfile
import unittest

from scpf.runner import run_script

ROOT = Path(__file__).resolve().parents[2]


class AssemblyTests(unittest.TestCase):
    def test_reusable_model_instances_compile_to_one_component_and_two_occurrences(self):
        commands = run_script(
            ROOT / "examples/components/scpf/model.py"
        )["commands"]

        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "parameters.add"],
            [],
        )
        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "component.create"],
            ["Block"],
        )
        copies = [c for c in commands if c["command"] == "occurrence.copy"]
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0]["params"]["component"], "Block")
        self.assertNotIn("translate", copies[0]["params"])
        placements = [c["params"] for c in commands if c["command"] == "occurrence.move"]
        self.assertEqual(placements[-1]["occurrence"], "Block:2")
        self.assertEqual(placements[-1]["translate"], [40.0, 0.0, 0.0])
        rectangle = next(
            c for c in commands
            if c["command"] == "sketch.rectangle.two_point"
        )
        self.assertNotIn("Block_length", str(rectangle["params"]))
        self.assertNotIn("Block_width", str(rectangle["params"]))

        joint = next(c for c in commands if c["command"] == "joint.create")
        self.assertEqual(joint["params"]["type"], "rigid")
        self.assertEqual(
            joint["params"]["a"],
            {"occurrence": "Block:1", "face": [20.0, 0.0, 5.0]},
        )
        self.assertEqual(
            joint["params"]["b"],
            {"occurrence": "Block:2", "face": [20.0, 0.0, 5.0]},
        )

    def test_copies_of_placed_occurrences_use_relative_native_offsets(self):
        """A copied occurrence inherits its source transform."""
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "sidewalls.py"
            script.write_text(
                "class SideWall:\n"
                "    def build(self):\n"
                "        return Box(15, 100, 362)\n"
                "class Cabinet:\n"
                "    def build(self):\n"
                "        left = SideWall().move(x=-429.5, y=25)\n"
                "        right = left.copy().move(x=859)\n"
                "        return (left + right).group('WoodBoxFrame')\n"
                "Cabinet()\n",
                encoding="utf-8",
            )
            commands = run_script(script)["commands"]
        copy = next(c["params"] for c in commands
                    if c["command"] == "occurrence.copy")
        self.assertEqual(copy["component"], "SideWall")
        self.assertNotIn("translate", copy)
        moves = [c["params"] for c in commands if c["command"] == "occurrence.move"]
        self.assertEqual([m["occurrence"] for m in moves], ["SideWall:1", "SideWall:2"])
        self.assertEqual(moves[0]["translate"], [-429.5, 25.0, 0.0])
        self.assertEqual(moves[1]["translate"], [429.5, 25.0, 0.0])

    def test_copy_resets_inherited_rotation_when_target_is_unrotated(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "rotated_source.py"
            script.write_text(
                "class Panel:\n"
                "    def build(self):\n"
                "        return Box(20, 10, 2)\n"
                "class Cabinet:\n"
                "    def build(self):\n"
                "        first = Panel().move(x=-40).rotate(degrees=180)\n"
                "        right = first.copy().move(x=80).rotate(degrees=0)\n"
                "        return first + right\n"
                "Cabinet()\n",
                encoding="utf-8",
            )
            commands = run_script(script)["commands"]
        copy = next(c["params"] for c in commands
                    if c["command"] == "occurrence.copy")
        self.assertNotIn("translate", copy)
        commands_after_component = [c for c in commands
                                    if c["command"] in ("occurrence.copy", "occurrence.move")]
        self.assertEqual([c["command"] for c in commands_after_component],
                         ["occurrence.copy", "occurrence.move", "occurrence.move"])
        moves = [c["params"] for c in commands_after_component[1:]]
        self.assertEqual([m["translate"] for m in moves],
                         [[-40.0, 0.0, 0.0], [40.0, 0.0, 0.0]])
        self.assertEqual([m["angle"] for m in moves], ["180 deg", "0 deg"])
        self.assertTrue(all("matrix" not in m and "to" not in m for m in moves))

    def test_named_group_creates_real_nested_native_component(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "group.py"
            path.write_text(
                "class Panel:\n"
                "    def build(self):\n"
                "        return Box(10, 2, 20)\n"
                "class Frame:\n"
                "    def build(self):\n"
                "        return Box(35, 10, 40)\n"
                "class Display:\n"
                "    def build(self):\n"
                "        left = Panel()\n"
                "        group = (left + left.copy().move(x=11)).group('HUB75Panels')\n"
                "        return group + Frame().move(y=20)\n"
                "Display()\n",
                encoding="utf-8",
            )
            commands = run_script(path)["commands"]
        created = [c["params"] for c in commands
                   if c["command"] == "component.create"]
        self.assertEqual([c["name"] for c in created],
                         ["HUB75Panels", "Panel", "Frame"])
        self.assertEqual(created[0]["activate"], False)
        self.assertTrue(created[0]["grounded"])
        self.assertEqual(created[1]["parent"], "HUB75Panels")
        self.assertFalse(created[1]["grounded"])
        self.assertNotIn("parent", created[2])
        copies = [c for c in commands if c["command"] == "occurrence.copy"]
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0]["params"]["component"], "Panel")

    def test_group_name_conflicts_and_multi_parent_definitions_rejected(self):
        from scpf.core import Box
        from scpf.model_objects import ModelDefinition, ModelInstance
        from scpf.assembly import compile_assembly
        from scpf.compiler import ModelError
        panel = ModelInstance(ModelDefinition("Panel", (), Box(10, 2, 20)))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            panel.group("")
        with self.assertRaisesRegex(ValueError, "multiple groups"):
            panel.group("One").group("Two")
        with self.assertRaisesRegex(ModelError, "multiple assembly parents"):
            compile_assembly(panel.group("A") + panel.copy(), "Display")
        with self.assertRaisesRegex(ModelError, "conflicts"):
            compile_assembly(panel.group("Panel"), "Display")

    def test_rotation_is_an_independent_occurrence_placement(self):
        from scpf.core import Box
        from scpf.model_objects import ModelDefinition, ModelInstance

        first = ModelInstance(ModelDefinition("Panel", (), Box(20, 10, 2)))
        second = first.copy().move(x=30).rotate(axis=(0, 0, 1), degrees=180)
        self.assertIs(first.definition, second.definition)
        self.assertIsNone(first.rotation)
        self.assertEqual(second.translation, (30, 0, 0))
        self.assertEqual(second.rotation, ((0.0, 0.0, 1.0), 180.0))
        self.assertIsNone(second.attachment)
        self.assertEqual(second.copy().rotation, second.rotation)
        self.assertEqual(second.move(x=10).translation, (40, 0, 0))

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rotation.py"
            path.write_text(
                "class Panel:\n"
                "    def build(self):\n"
                "        return Box(20, 10, 2)\n"
                "class Display:\n"
                "    def build(self):\n"
                "        first = Panel()\n"
                "        return first + first.copy().move(x=30).rotate(degrees=180)\n"
                "Display()\n",
                encoding="utf-8",
            )
            commands = run_script(path)["commands"]

        self.assertEqual(len([c for c in commands if c["command"] == "component.create"]), 1)
        self.assertEqual(len([c for c in commands if c["command"] == "occurrence.copy"]), 1)
        rotated = [c["params"] for c in commands if c["command"] == "occurrence.move"]
        self.assertEqual(len(rotated), 1)
        self.assertEqual(rotated[0]["occurrence"], "Panel:2")
        self.assertNotIn("to", rotated[0])
        self.assertEqual(rotated[0]["translate"], [30.0, 0.0, 0.0])
        self.assertEqual(rotated[0]["axis"], [0.0, 0.0, 1.0])
        self.assertEqual(rotated[0]["angle"], "180 deg")
        self.assertNotIn("matrix", rotated[0])

    def test_named_axis_rotation_shorthand(self):
        from scpf.core import Box, X, Y, Z
        from scpf.model_objects import ModelDefinition, ModelInstance

        panel = ModelInstance(ModelDefinition("Panel", (), Box(20, 10, 2)))

        self.assertEqual(
            panel.rotate(X, 180).rotation,
            ((1.0, 0.0, 0.0), 180.0),
        )
        self.assertEqual(
            panel.rotate(Y, 90).rotation,
            ((0.0, 1.0, 0.0), 90.0),
        )
        self.assertEqual(
            panel.rotate(Z, -90).rotation,
            ((0.0, 0.0, 1.0), -90.0),
        )

        with self.assertRaisesRegex(ValueError, "X, Y or Z"):
            panel.rotate("Q", 90)

    def test_first_grounded_occurrence_can_have_absolute_rotation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "root_rotation.py"
            path.write_text(
                "class Panel:\n"
                "    def build(self):\n"
                "        return Box(20, 10, 2)\n"
                "class Display:\n"
                "    def build(self):\n"
                "        first = Panel().move(x=-50).rotate(degrees=180)\n"
                "        return first + first.copy().move(x=50).rotate(degrees=0)\n"
                "Display()\n", encoding="utf-8",
            )
            commands = run_script(path)["commands"]
        placements = [c["params"] for c in commands if c["command"] == "occurrence.move"]
        self.assertEqual(len(placements), 2)
        self.assertEqual(placements[0]["occurrence"], "Panel:1")
        self.assertTrue(placements[0]["move_grounded"])
        self.assertEqual(placements[0]["translate"], [-50.0, 0.0, 0.0])
        self.assertEqual(placements[1]["translate"], [0.0, 0.0, 0.0])
        self.assertEqual([m["angle"] for m in placements], ["180 deg", "0 deg"])

    def test_explicit_imported_component_factory(self):
        # The library's scpf/ source folder is a namespace root when the
        # test runner executes from the repository root. Import the module
        # directly here; the external-package public import is checked in CI.
        from scpf.runner import component
        from scpf.model_objects import ModelInstance

        class LibraryPanel:
            width = 20

            def build(self):
                from scpf.core import Box
                return Box(self.width, 10, 2)

        Panel = component(LibraryPanel)
        first = Panel()
        second = Panel().move(x=20)
        self.assertIsInstance(first, ModelInstance)
        self.assertIsInstance(second, ModelInstance)
        self.assertEqual(first.definition.key, second.definition.key)
        self.assertEqual(second.translation, (20, 0, 0))
        with self.assertRaisesRegex(TypeError, "model class"):
            component(42)

    def test_copies_start_at_origin_before_any_native_placement(self):
        """Five copies: only native SolidCraft operations, no matrix algebra."""
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "five.py"
            script.write_text(
                "class Panel:\n"
                "    def build(self):\n"
                "        return Box(159.7, 319.71, 14.5)\n"
                "class Screen:\n"
                "    def build(self):\n"
                "        first = Panel().move(z=160).rotate(axis=(1,0,0), degrees=90)\n"
                "        return (first + first.copy().move(x=-320) +\n"
                "                first.copy().move(x=-160) +\n"
                "                first.copy().move(x=160) +\n"
                "                first.copy().move(x=320))\n"
                "Screen()\n",
                encoding="utf-8",
            )
            commands = run_script(script)["commands"]
        placements = [c for c in commands if c["command"] in (
            "occurrence.copy", "occurrence.move")]
        self.assertEqual([c["command"] for c in placements],
                         ["occurrence.copy"] * 4 + ["occurrence.move"] * 5)
        self.assertTrue(all(c["params"] == {"component": "Panel"}
                            for c in placements[:4]))
        self.assertEqual([c["params"]["translate"] for c in placements[4:]],
                         [[0.0, 0.0, 160.0], [-320.0, 0.0, 160.0],
                          [-160.0, 0.0, 160.0], [160.0, 0.0, 160.0],
                          [320.0, 0.0, 160.0]])
        self.assertTrue(all(c["params"]["axis"] == [1.,0.,0.]
                            and c["params"]["angle"] == "90 deg"
                            for c in placements[4:]))
        self.assertTrue(all("matrix" not in c["params"]
                            and "to" not in c["params"]
                            for c in placements))

    def test_rotation_rejects_undefined_and_nonfinite_axis_angle(self):
        from scpf.core import Box
        from scpf.model_objects import ModelDefinition, ModelInstance

        panel = ModelInstance(ModelDefinition("Panel", (), Box(2, 2, 1)))
        for kwargs in (
            {"axis": (0, 0, 0), "degrees": 90},
            {"axis": (0, 1), "degrees": 90},
            {"axis": (0, float("nan"), 1), "degrees": 90},
            {"axis": (0, 0, 1), "degrees": float("inf")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                panel.rotate(**kwargs)

    def test_component_attach_rejects_non_associative_offset_for_now(self):
        from scpf.core import Anchor
        from scpf.model_objects import ModelDefinition, ModelInstance
        from scpf.core import Box

        definition = ModelDefinition(
            "Block",
            (("length", 40.0), ("width", 30.0), ("height", 10.0)),
            Box(40, 30, 10),
        )
        left = ModelInstance(definition)
        right = ModelInstance(definition)

        with self.assertRaisesRegex(ValueError, "not implemented associatively"):
            right.attach(
                left,
                parent=Anchor.RIGHT,
                child=Anchor.LEFT,
                offset=(5, 0),
            )

    def test_different_model_parameters_create_independent_component_definitions(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "class Block:\n"
                "    length = 40.0\n"
                "    width = 30.0\n"
                "    height = 10.0\n"
                "    def build(self):\n"
                "        Box(self.length, self.width, self.height)\n"
                "class Pair:\n"
                "    def build(self):\n"
                "        left = Block(width=30.0)\n"
                "        right = Block(width=50.0).move(x=60.0)\n"
                "        left + right\n"
                "Pair()\n"
            )
            commands = run_script(file)["commands"]

        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "component.create"],
            ["Block", "Block 2"],
        )
        self.assertFalse(any(c["command"] == "occurrence.copy" for c in commands))
        parameter_names = [
            c["params"]["name"] for c in commands
            if c["command"] == "parameters.add"
        ]
        self.assertEqual(parameter_names, [])


    def test_component_defaults_are_fixed_unless_included(self):
        from scpf.assembly import compile_assembly
        from scpf.core import Box
        from scpf.runner import component

        class Bracket:
            width = 24.0
            radius = 4.0
            chamfer = 2.0

            def build(self):
                return Box(
                    self.width,
                    self.radius + 20,
                    self.chamfer + 10,
                )

        Hidden = component(Bracket)
        hidden = compile_assembly(Hidden(), "Hidden")["commands"]
        hidden_names = [
            command["params"]["name"]
            for command in hidden
            if command["command"] == "parameters.add"
        ]
        self.assertEqual(hidden_names, [])

        Selected = component(Bracket, include=("radius",))
        selected = compile_assembly(Selected(), "Selected")["commands"]
        selected_names = [
            command["params"]["name"]
            for command in selected
            if command["command"] == "parameters.add"
        ]
        self.assertEqual(selected_names, ["Bracket_radius"])

        All = component(Bracket, include="*")
        all_commands = compile_assembly(All(), "All")["commands"]
        all_names = [
            command["params"]["name"]
            for command in all_commands
            if command["command"] == "parameters.add"
        ]
        self.assertEqual(
            all_names,
            ["Bracket_width", "Bracket_radius", "Bracket_chamfer"],
        )

        with self.assertRaisesRegex(ValueError, "unknown component parameter"):
            component(Bracket, include=("missing",))

    def test_component_decorator_accepts_selected_include(self):
        from scpf.assembly import compile_assembly
        from scpf.core import Box
        from scpf.runner import component

        @component(include=("radius",))
        class Bracket:
            width = 24.0
            radius = 4.0

            def build(self):
                return Box(self.width, self.radius + 20, 10)

        commands = compile_assembly(Bracket(), "BracketAssembly")["commands"]
        names = [
            command["params"]["name"]
            for command in commands
            if command["command"] == "parameters.add"
        ]
        self.assertEqual(names, ["Bracket_radius"])

    def test_component_preserves_parent_parameter_dependency(self):
        from scpf.assembly import compile_assembly
        from scpf.core import Box, Parameter
        from scpf.runner import component

        class Panel:
            width = 100.0
            height = 20.0
            thickness = 2.0

            def build(self):
                return Box(self.width, self.thickness, self.height)

        PanelObject = component(Panel)
        parent_width = Parameter("opening_width", 844.0)
        instance = PanelObject(width=parent_width)

        self.assertNotIn("width", dict(instance.definition.parameters))
        self.assertEqual(
            dict(instance.definition.external_parameters)["opening_width"],
            844.0,
        )
        self.assertEqual(
            dict(instance.definition.input_bindings)["width"],
            "opening_width",
        )
        self.assertEqual(
            instance.definition.shape.data[0].name,
            "opening_width",
        )

        commands = compile_assembly(instance, "Display")["commands"]
        parameter_names = [
            command["params"]["name"]
            for command in commands
            if command["command"] == "parameters.add"
        ]
        self.assertIn("opening_width", parameter_names)
        self.assertNotIn("Panel_width", parameter_names)

    def test_shared_parent_parameter_is_added_once_for_multiple_components(self):
        from scpf.assembly import compile_assembly
        from scpf.core import Box, Parameter
        from scpf.runner import component

        class Strip:
            length = 100.0
            width = 12.0

            def build(self):
                return Box(self.length, self.width, 4)

        StripObject = component(Strip)
        opening_width = Parameter("opening_width", 844.0)

        horizontal = StripObject(length=opening_width, width=12.0)
        second = StripObject(length=opening_width, width=15.0).move(y=20)

        commands = compile_assembly(horizontal + second, "Frame")["commands"]
        parameter_names = [
            command["params"]["name"]
            for command in commands
            if command["command"] == "parameters.add"
        ]

        self.assertEqual(parameter_names.count("opening_width"), 1)
        self.assertNotIn("Strip_length", parameter_names)
        self.assertNotIn("Strip_2_length", parameter_names)
        self.assertNotIn("Strip_width", parameter_names)
        self.assertNotIn("Strip_2_width", parameter_names)

    def test_parent_expression_remains_an_expression_in_child_geometry(self):
        from scpf.assembly import compile_assembly
        from scpf.core import Box, Parameter
        from scpf.runner import component

        class Board:
            width = 100.0
            thickness = 12.0

            def build(self):
                return Box(self.width, 50, self.thickness)

        BoardObject = component(Board)
        opening_width = Parameter("opening_width", 844.0)
        frame_wood_thickness = Parameter("frame_wood_thickness", 12.0)
        outer_width = opening_width + 2 * frame_wood_thickness

        board = BoardObject(width=outer_width)
        commands = compile_assembly(board, "Frame")["commands"]

        parameter_names = [
            command["params"]["name"]
            for command in commands
            if command["command"] == "parameters.add"
        ]
        self.assertEqual(parameter_names.count("opening_width"), 1)
        self.assertEqual(parameter_names.count("frame_wood_thickness"), 1)
        self.assertNotIn("Board_width", parameter_names)

        rectangle = next(
            command for command in commands
            if command["command"] == "sketch.rectangle.two_point"
        )
        self.assertIn("opening_width", str(rectangle["params"]))
        self.assertIn("frame_wood_thickness", str(rectangle["params"]))

    def test_imported_assembly_class_uses_object_syntax(self):
        from scpf.core import Box, Parameter
        from scpf.runner import assembly, component
        from scpf.model_objects import Assembly

        class Panel:
            width = 100.0
            height = 20.0
            thickness = 2.0

            def build(self):
                return Box(self.width, self.thickness, self.height)

        PanelObject = component(Panel)

        class PanelRow:
            width = 100.0
            pitch = 110.0

            def build(self):
                left = PanelObject(width=self.width)
                right = left.copy().move(x=self.pitch)
                return (left + right).group("Panels")

        PanelRowObject = assembly(PanelRow)
        row = PanelRowObject(
            width=Parameter("panel_width", 160.0),
            pitch=Parameter("panel_pitch", 170.0),
        )

        self.assertIsInstance(row, Assembly)
        self.assertEqual(len(row.instances), 2)
        self.assertEqual(row.instances[1].translation, (170.0, 0.0, 0.0))
        self.assertNotIn(
            "width",
            dict(row.instances[0].definition.parameters),
        )
        self.assertEqual(
            dict(row.instances[0].definition.external_parameters)["panel_width"],
            160.0,
        )


if __name__ == "__main__":
    unittest.main()
