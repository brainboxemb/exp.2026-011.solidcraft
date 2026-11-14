"""Qualification tests for the primitive CSG case."""
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class PrimitiveCsgCommandTests(unittest.TestCase):
    def test_generated_command_contract(self):
        commands = run_script(
            ROOT / "examples/primitive-csg/scpf/model.py"
        )["commands"]

        self.assertEqual(
            [command["command"] for command in commands],
            ["solid.sphere", "solid.box", "solid.cylinder", "solid.box"],
        )

        sphere = commands[0]["params"]
        joined_box = commands[1]["params"]
        cylinder = commands[2]["params"]
        clipped_box = commands[3]["params"]

        self.assertEqual(sphere["operation"], "new")
        self.assertEqual(sphere["radius"], 20)
        self.assertEqual(joined_box["operation"], "join")
        self.assertEqual(joined_box["center"], [18.0, 0.0, 10.0])

        self.assertEqual(cylinder["operation"], "cut")
        self.assertEqual(cylinder["axis"], "X")
        self.assertEqual(cylinder["diameter"], 8)
        self.assertEqual(cylinder["height"], 60)
        self.assertEqual(cylinder["base"], [-30, 0, 0])

        self.assertEqual(clipped_box["operation"], "intersect")
        self.assertEqual(clipped_box["center"], [0.0, 0.0, 15.0])


if __name__ == "__main__":
    unittest.main()
