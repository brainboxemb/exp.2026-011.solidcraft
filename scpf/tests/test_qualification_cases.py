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

        sphere, joined_box, *rest = [command["params"] for command in commands]
        cylinders = rest[:3]
        clipped_box = rest[3]

        self.assertEqual(sphere["operation"], "new")
        self.assertEqual(joined_box["operation"], "join")
        self.assertEqual(joined_box["center"], [18.0, 0.0, 10.0])

        self.assertEqual([row["axis"] for row in cylinders], ["X", "Y", "Z"])
        self.assertTrue(all(row["operation"] == "cut" for row in cylinders))
        self.assertTrue(all(row["diameter"] == 8 for row in cylinders))
        self.assertTrue(all(row["height"] == 60 for row in cylinders))

        self.assertEqual(clipped_box["operation"], "intersect")
        self.assertEqual(clipped_box["center"], [0.0, 0.0, 15.0])


if __name__ == "__main__":
    unittest.main()
