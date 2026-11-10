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

    def test_script_requires_final_model_expression(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "model.py"
            file.write_text("def CubeModel(size=50):\n    return Cube(size)\n")
            with self.assertRaises(SyntaxError):
                run_script(file)


if __name__ == "__main__":
    unittest.main()
