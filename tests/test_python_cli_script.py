"""Offline tests of the small Python-to-SolidCraft JSON script builder."""
import unittest
from examples.python_cli_script import bracket_commands


class ScriptBuilderTests(unittest.TestCase):
    def test_commands_have_expected_sequence(self):
        commands = bracket_commands()["commands"]
        self.assertEqual(
            [c["command"] for c in commands],
            ["parameters.change", "sketch.create", "sketch.line",
             "sketch.finish", "solid.extrude"],
        )
        self.assertEqual(commands[2]["params"]["points"],
                         [[0, 0], [40, 0], [40, 6],
                          [6, 6], [6, 30], [0, 30]])
        self.assertEqual(commands[4]["params"]["distance"], "width")

    def test_parameters_change_generated_geometry(self):
        commands = bracket_commands(arm_x=48, arm_z=35,
                                    wall=8, width=75)["commands"]
        self.assertEqual(commands[0]["params"]["expression"], "75 mm")
        self.assertEqual(commands[2]["params"]["points"][2], [48, 8])
        self.assertEqual(commands[2]["params"]["points"][4], [8, 35])

    def test_invalid_dimensions_refused(self):
        with self.assertRaises(ValueError):
            bracket_commands(wall=0)
        with self.assertRaises(ValueError):
            bracket_commands(wall=40)


if __name__ == "__main__":
    unittest.main()
