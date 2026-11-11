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
            ["Block_length", "Block_width", "Block_height"],
        )
        self.assertEqual(
            [c["params"]["name"] for c in commands
             if c["command"] == "component.create"],
            ["Block"],
        )
        copies = [c for c in commands if c["command"] == "occurrence.copy"]
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0]["params"]["component"], "Block")
        self.assertEqual(copies[0]["params"]["translate"], [40.0, 0.0, 0.0])
        rectangle = next(
            c for c in commands
            if c["command"] == "sketch.rectangle.two_point"
        )
        self.assertIn("Block_length", str(rectangle["params"]))
        self.assertIn("Block_width", str(rectangle["params"]))

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
        self.assertEqual(
            parameter_names,
            [
                "Block_length", "Block_width", "Block_height",
                "Block_2_length", "Block_2_width", "Block_2_height",
            ],
        )


if __name__ == "__main__":
    unittest.main()
