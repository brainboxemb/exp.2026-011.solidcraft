"""Focused command-contract regressions for documented qualification cases."""
from pathlib import Path
import runpy
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
        self.assertEqual(cylinder["axis"], "Z")
        self.assertEqual(cylinder["diameter"], 8)
        self.assertEqual(cylinder["height"], 60)
        self.assertEqual(cylinder["base"], [0.0, 0.0, -30.0])

        self.assertEqual(clipped_box["operation"], "intersect")
        self.assertEqual(clipped_box["center"], [0.0, 0.0, 15.0])

    def test_parameter_scope_command_contract(self):
        document = run_script(
            ROOT / "examples/parameter-scope/scpf/model.py"
        )
        verifier = runpy.run_path(
            str(ROOT / "qualification/parameter_scope.py")
        )
        verifier["check_command_document"](document)


if __name__ == "__main__":
    unittest.main()
