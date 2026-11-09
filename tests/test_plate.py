"""Offline checks of our fixture's geometry commands (no SolidCraft needed)."""

import unittest
from unittest.mock import Mock

from examples.plate import construct_plate


class PlateCommandTests(unittest.TestCase):
    def setUp(self):
        self.cad = Mock()
        self.cad.sketch.rectangle_center.return_value = {
            "curves": ["edge-1", "edge-2", "edge-3", "edge-4"]
        }

    def test_plate_outline_hole_and_extrusion(self):
        construct_plate(self.cad)
        self.cad.sketch.create.assert_called_once_with(plane="XY", name="Plate")
        self.cad.sketch.rectangle_center.assert_called_once_with(
            center=(0, 0), corner=(50, 30)
        )
        self.cad.sketch.circle_center.assert_called_once_with(
            center=(0, 0), diameter=20
        )
        self.cad.sketch.finish.assert_called_once_with()
        self.cad.solid.extrude.assert_called_once_with(
            distance=10,
            profiles=[{"curves": ["edge-1", "edge-2", "edge-3", "edge-4"]}],
            body_name="Plate",
        )

    def test_parameters_change_geometry(self):
        construct_plate(self.cad, length=120, width=40, thickness=5,
                        hole_diameter=12)
        self.cad.sketch.rectangle_center.assert_called_once_with(
            center=(0, 0), corner=(60, 20)
        )
        self.cad.sketch.circle_center.assert_called_once_with(
            center=(0, 0), diameter=12
        )
        self.cad.solid.extrude.assert_called_once_with(
            distance=5,
            profiles=[{"curves": ["edge-1", "edge-2", "edge-3", "edge-4"]}],
            body_name="Plate",
        )

    def test_rejects_hole_that_does_not_fit(self):
        with self.assertRaisesRegex(ValueError, "fit"):
            construct_plate(self.cad, width=10, hole_diameter=10)
        self.cad.sketch.create.assert_not_called()

    def test_rejects_nonpositive_dimensions(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            construct_plate(self.cad, thickness=0)
        self.cad.sketch.create.assert_not_called()

    def test_missing_curve_ids_aborts_before_extrusion(self):
        self.cad.sketch.rectangle_center.return_value = {}
        with self.assertRaisesRegex(RuntimeError, "curve IDs"):
            construct_plate(self.cad)
        self.cad.solid.extrude.assert_not_called()


if __name__ == "__main__":
    unittest.main()
