"""Regression checks for the standalone CornerBracket example."""
from pathlib import Path
import unittest

from scpf.runner import run_script

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "corner-bracket" / "scpf"


class CornerBracketTests(unittest.TestCase):
    def test_default_is_fast_four_countersinks(self):
        commands = run_script(EXAMPLE / "model.py")["commands"]
        holes = [c for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 4)
        self.assertTrue(all(c["params"].get("type") == "countersink" for c in holes))
        self.assertEqual(len([c for c in commands if c["command"] == "solid.chamfer"]), 2)
        self.assertEqual(len([c for c in commands if c["command"] == "solid.fillet"]), 1)
        # 19 params + 4 sketch+extrude + 3 edge modifiers + 4 holes.
        self.assertEqual(len(commands), 30)

    def test_original_reference_kept_separate(self):
        commands = run_script(EXAMPLE / "model_reference.py")["commands"]
        holes = [c for c in commands if c["command"] == "solid.hole"]
        self.assertEqual(len(holes), 16)
        self.assertEqual(len(commands), 42)


if __name__ == "__main__":
    unittest.main()
