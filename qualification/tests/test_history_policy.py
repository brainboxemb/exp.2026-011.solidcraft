"""Qualification contract for compiler history policy."""

from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]


class HistoryPolicyCommandTests(unittest.TestCase):
    def test_auto_and_sketch_policies_lower_differently(self):
        commands = run_script(
            ROOT / "examples/history-policy/scpf/model.py"
        )["commands"]

        native_boss = [
            row for row in commands
            if row["command"] == "plastic.boss"
        ]
        self.assertEqual(len(native_boss), 2)
        self.assertEqual(
            [row["params"]["position"] for row in native_boss],
            [[-10.0, 0.0, 6.0], [0.0, 15.0, 6.0]],
        )

        sketches = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "sketch.create"
        ]
        self.assertIn("Boss", sketches)
        self.assertIn("Boss hole", sketches)
        self.assertIn("Explicit pad", sketches)

        extrudes = [
            row["params"]
            for row in commands
            if row["command"] == "solid.extrude"
        ]
        boss_join = next(row for row in extrudes if row.get("name") == "Boss")
        boss_cut = next(row for row in extrudes if row.get("name") == "Boss hole")
        explicit_pad = next(row for row in extrudes if row.get("name") == "Explicit pad")

        self.assertEqual(boss_join["operation"], "join")
        self.assertEqual(boss_join["direction"], "positive")
        self.assertEqual(boss_cut["operation"], "cut")
        self.assertEqual(boss_cut["direction"], "negative")
        self.assertEqual(explicit_pad["operation"], "join")
        self.assertEqual(explicit_pad["direction"], "positive")


if __name__ == "__main__":
    unittest.main()
