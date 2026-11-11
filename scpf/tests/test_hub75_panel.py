"""First real-model regression for SCPF reusable components."""
import unittest
from pathlib import Path

from scpf.runner import run_script

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "examples/hub75-panel/scpf/model.py"


class Hub75PanelTests(unittest.TestCase):
    def test_two_placements_share_one_component_definition(self):
        commands = run_script(MODEL)["commands"]
        def of(kind):
            return [c["params"] for c in commands if c["command"] == kind]

        self.assertEqual([c["name"] for c in of("component.create")], ["Hub75Panel"])
        copies = of("occurrence.copy")
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0]["component"], "Hub75Panel")
        self.assertEqual(copies[0]["translate"], [160.0, 0.0, 0.0])
        self.assertEqual(of("joint.create"), [])
        self.assertEqual(len(of("solid.hole")), 6)
        self.assertEqual(
            [c["name"] for c in of("parameters.add")],
            ["Hub75Panel_width", "Hub75Panel_height", "Hub75Panel_depth",
             "Hub75Panel_mount_x", "Hub75Panel_mount_y", "Hub75Panel_hole_diameter"],
        )

    def test_mount_positions_match_source_drawing(self):
        commands = run_script(MODEL)["commands"]
        holes = [c["params"] for c in commands if c["command"] == "solid.hole"]
        # Parameter expressions may be retained by the native compiler.
        positions = [h["position"] for h in holes]
        self.assertEqual(len(positions), 6)
        self.assertEqual(len({str(p) for p in positions}), 6)
        self.assertTrue(all(h["direction"] == [0, 0, -1] for h in holes))
        self.assertTrue(all(h["targets"] == ["Hub75Panel"] for h in holes))

    def test_material_is_native_and_housing_color_is_grey(self):
        commands = run_script(MODEL)["commands"]
        material = next(c["params"] for c in commands if c["command"] == "material.create")
        self.assertEqual(material["color"], "#B8B8B8")
        assigned = next(c["params"] for c in commands if c["command"] == "material.assign")
        self.assertEqual(assigned["bodies"], ["Hub75Panel"])


if __name__ == "__main__":
    unittest.main()
