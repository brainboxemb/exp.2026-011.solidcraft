"""Qualification contract for the public @assembly decorator."""

import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class AssemblyDecoratorCommandTests(unittest.TestCase):
    def test_imported_assembly_lowers_to_reusable_native_occurrences(self):
        commands = run_script(
            ROOT / "examples/assembly-decorator/scpf/model.py"
        )["commands"]

        created = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(created, ["Post"])

        copies = [
            row["params"]
            for row in commands
            if row["command"] == "occurrence.copy"
        ]
        self.assertEqual(copies, [{"component": "Post"}])

        moves = [
            row["params"]
            for row in commands
            if row["command"] == "occurrence.move"
        ]
        self.assertEqual(
            [(row["occurrence"], row["translate"]) for row in moves],
            [
                ("Post:1", [-15.0, 0.0, 0.0]),
                ("Post:2", [15.0, 0.0, 0.0]),
            ],
        )


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class AssemblyDecoratorNativeTests(unittest.TestCase):
    def test_imported_assembly_builds_two_posts(self):
        data = json.loads(
            (
                Path(NATIVE_ROOT)
                / "assembly-decorator"
                / "measurements.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(data["body_count"], 2)
        actual = sorted(
            (body["bbox"]["min"], body["bbox"]["max"])
            for body in data["bodies"]
        )
        self.assertEqual(
            actual,
            sorted([
                ([-20.0, -5.0, 0.0], [-10.0, 5.0, 20.0]),
                ([10.0, -5.0, 0.0], [20.0, 5.0, 20.0]),
            ]),
        )


if __name__ == "__main__":
    unittest.main()
