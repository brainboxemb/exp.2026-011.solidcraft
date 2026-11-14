"""Qualification contract for parent-derived child dimensions."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class ParentDerivedChildSizeCommandTests(unittest.TestCase):
    def test_child_dimensions_keep_parent_expressions(self):
        document = run_script(
            ROOT / "examples/parent-derived-child-size/scpf/model.py"
        )
        commands = document["commands"]

        parameters = [
            row["params"]
            for row in commands
            if row["command"] == "parameters.add"
        ]
        self.assertEqual(
            [(row["name"], row["expression"]) for row in parameters],
            [
                ("base_width", "120"),
                ("base_depth", "80"),
            ],
        )

        rectangles = [
            row["params"]
            for row in commands
            if row["command"] == "sketch.rectangle.two_point"
        ]
        self.assertEqual(len(rectangles), 2)

        expressions = {
            (row["p0"][0], row["p1"][0], row["p0"][1], row["p1"][1])
            for row in rectangles
        }
        self.assertIn(
            (
                "-base_width / 2",
                "base_width / 2",
                "-base_depth / 2",
                "base_depth / 2",
            ),
            expressions,
        )
        self.assertIn(
            (
                "-(base_width / 2) / 2",
                "(base_width / 2) / 2",
                "-(base_depth / 2) / 2",
                "(base_depth / 2) / 2",
            ),
            expressions,
        )

        components = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["ParentBlock", "DerivedChild"])


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class ParentDerivedChildSizeNativeTests(unittest.TestCase):
    def test_baseline_dimensions(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "parent-derived-child-size"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 2)
        self.assertEqual(
            _sizes(data),
            [(60.0, 40.0, 6.0), (120.0, 80.0, 10.0)],
        )

    def test_parent_resize_rebuilds_child_dimensions(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "parent-derived-child-size"
            / "measurements-size-160x120.json"
        )
        self.assertEqual(
            {row["name"]: row["value"] for row in data["params"]},
            {
                "base_width": 160.0,
                "base_depth": 120.0,
            },
        )
        self.assertEqual(
            _sizes(data),
            [(80.0, 60.0, 6.0), (160.0, 120.0, 10.0)],
        )


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sizes(data):
    return sorted(
        tuple(
            round(hi - lo, 6)
            for lo, hi in zip(body["bbox"]["min"], body["bbox"]["max"])
        )
        for body in data["bodies"]
    )


if __name__ == "__main__":
    unittest.main()
