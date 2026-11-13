"""Focused command-contract regressions for documented qualification cases."""
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class QualificationCaseTests(unittest.TestCase):
    def test_primitive_csg_command_contract(self):
        commands = run_script(
            ROOT / "examples/primitive-csg/scpf/model.py"
        )["commands"]

        self.assertEqual(
            [command["command"] for command in commands],
            [
                "solid.sphere",
                "solid.box",
                "solid.cylinder",
                "solid.cylinder",
                "solid.cylinder",
                "solid.box",
            ],
        )

        sphere = commands[0]["params"]
        joined_box = commands[1]["params"]
        cylinders = [command["params"] for command in commands[2:5]]
        clipped_box = commands[5]["params"]

        self.assertEqual(sphere["operation"], "new")
        self.assertEqual(sphere["radius"], 20)

        self.assertEqual(joined_box["operation"], "join")
        self.assertEqual(joined_box["center"], [18.0, 0.0, 10.0])

        self.assertEqual([row["axis"] for row in cylinders], ["X", "Y", "Z"])
        self.assertTrue(all(row["operation"] == "cut" for row in cylinders))
        self.assertTrue(all(row["diameter"] == 8 for row in cylinders))
        self.assertTrue(all(row["height"] == 60 for row in cylinders))
        self.assertEqual(
            [row["base"] for row in cylinders],
            [[-30.0, 0, 0], [0, -30.0, 0], [0, 0, -30.0]],
        )

        self.assertEqual(clipped_box["operation"], "intersect")
        self.assertEqual(clipped_box["center"], [0.0, 0.0, 15.0])


if __name__ == "__main__":
    unittest.main()
