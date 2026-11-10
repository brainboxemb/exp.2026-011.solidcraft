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
        expected = json.loads((ROOT / "examples/csg-cube/solidcraftforge/solidcraft.json").read_text())
        self.assertEqual(generated, expected)
        self.assertEqual(generated["commands"][0]["params"]["name"], "size")
        self.assertEqual(generated["commands"][1]["params"]["radius"], "size / 1.5")

    def test_plate_matches_reviewed_native_commands(self):
        generated = run_script(ROOT / "examples/plate/scpf/model.py")
        expected = json.loads((ROOT / "examples/plate/solidcraftforge/solidcraft.json").read_text())
        self.assertEqual(generated, expected)
        self.assertEqual([c["params"]["name"] for c in generated["commands"][:3]],
                         ["length", "width", "thickness"])
        centers = [
            c["params"]["center"]
            for c in generated["commands"]
            if c["command"] == "sketch.circle.center"
        ]
        self.assertEqual(centers, [[-35, -15], [35, -15], [35, 15], [-35, 15]])

    def test_arguments_are_editable_without_decorators(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def CsgCube(size=50.0):\n"
                "    return Sphere(size / 1.5) & Cube(size)\n"
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
                "    return body - Cylinder(3, 8).pattern(x=70, y=30)\n"
                "Plate()\n"
            )
            with self.assertRaises(ModelError):
                run_script(file)

    def test_move_translates_a_csg_composite_without_changing_sizes(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text(
                "def CsgCube(size=50.0):\n"
                "    body = Sphere(size / 1.5) & Cube(size)\n"
                "    holes = Cylinder(size, size / 1.5).orient(X, Y, Z)\n"
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
                "    return Cube(size).move(x=float('nan'))\n"
                "Cuboid()\n"
            )
            with self.assertRaises(ValueError):
                run_script(file)

    def test_script_requires_final_model_expression(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text("def CubeModel(size=50):\n    return Cube(size)\n")
            with self.assertRaises(SyntaxError):
                run_script(file)


if __name__ == "__main__":
    unittest.main()
