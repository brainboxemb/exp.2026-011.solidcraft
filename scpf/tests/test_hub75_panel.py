"""First real-model regression for SCPF reusable components."""
import unittest
from pathlib import Path

from scpf.runner import run_script

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "examples/hub75-panel/scpf/model.py"


class Hub75PanelTests(unittest.TestCase):
    def test_copy_creates_a_second_occurrence_of_one_definition(self):
        from scpf.core import Box
        from scpf.model_objects import ModelDefinition, ModelInstance

        original = ModelInstance(ModelDefinition("Panel", (), Box(20, 10, 2)))
        duplicate = original.copy().move(x=24)
        self.assertIsNot(original, duplicate)
        self.assertIs(original.definition, duplicate.definition)
        self.assertEqual(original.translation, (0, 0, 0))
        self.assertEqual(duplicate.translation, (24, 0, 0))
        self.assertIsNone(duplicate.attachment)

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
             "Hub75Panel_front_depth", "Hub75Panel_rear_inset",
             "Hub75Panel_hole_diameter", "Hub75Panel_mount_x", "Hub75Panel_mount_y"],
        )

    def test_rear_taper_uses_editable_native_loft(self):
        commands = run_script(MODEL)["commands"]
        kinds = [c["command"] for c in commands]
        self.assertEqual(kinds.count("solid.extrude"), 1)
        self.assertEqual(kinds.count("solid.loft"), 1)
        self.assertEqual(kinds.count("sketch.rectangle.two_point"), 3)
        loft = next(c["params"] for c in commands if c["command"] == "solid.loft")
        self.assertEqual(loft["operation"], "join")
        self.assertEqual(loft["targets"], ["Hub75Panel"])
        self.assertIn("rear start", loft["sections"][0]["sketch"])
        self.assertIn("rear perimeter", loft["sections"][1]["sketch"])
        planes = [c["params"] for c in commands if c["command"] == "sketch.create"]
        self.assertEqual(
            [p.get("offset", 0) for p in planes],
            [0, "Hub75Panel_front_depth", "Hub75Panel_depth"],
        )

    def test_taper_rejects_invalid_dimensions(self):
        from scpf.core import Box
        for kwargs in (
            {"from_z": 0, "inset": 1.25},
            {"from_z": 20, "inset": 1.25},
            {"from_z": 2, "inset": 100},
            {"from_z": 2, "inset": 0},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Box(159.70, 319.71, 14.50).taper(**kwargs)

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
