"""Regression tests for fixed qualification cameras and goal projection."""
from pathlib import Path
import base64
from io import BytesIO
import json
import sys
import tempfile
import zlib
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qualification.camera import camera
from qualification.goal_overlay import _project, render
from qualification.visual_validation import REFERENCE_SIZE, decode_reference


class QualificationCameraTests(unittest.TestCase):
    def test_front_camera_uses_supported_solidcraft_schema(self):
        measurements = {
            "bodies": [
                {"bbox": {"min": [-20, -15, 0], "max": [20, 15, 10]}}
            ]
        }

        value = camera(measurements, "front")

        self.assertEqual(value["target"], [0.0, 0.0, 5.0])
        self.assertEqual(value["yaw"], 0.0)
        self.assertEqual(value["pitch"], 0.0)
        self.assertEqual(value["fov"], 0.0)
        self.assertNotIn("up", value)

    def test_front_projection_maps_x_right_and_z_up(self):
        value = {
            "target": [0.0, 0.0, 0.0],
            "yaw": 0.0,
            "pitch": 0.0,
            "roll": 0.0,
            "distance": 100.0,
            "fov": 0.0,
        }

        center = _project((0, 0, 0), value, 800, 600)
        right = _project((10, 0, 0), value, 800, 600)
        up = _project((0, 0, 10), value, 800, 600)

        self.assertAlmostEqual(center[0], 400.0)
        self.assertAlmostEqual(center[1], 300.0)
        self.assertGreater(right[0], center[0])
        self.assertAlmostEqual(right[1], center[1])
        self.assertLess(up[1], center[1])
        self.assertAlmostEqual(up[0], center[0])

    def test_png_baseline_is_normalized_for_comparison(self):
        source = Image.new("RGB", (240, 180), (90, 120, 150))
        payload = BytesIO()
        source.save(payload, format="PNG")

        reference = decode_reference({
            "png_base64": base64.b64encode(payload.getvalue()).decode("ascii")
        })

        self.assertEqual(reference.size, REFERENCE_SIZE)
        self.assertEqual(reference.mode, "L")

    def test_compressed_pixel_baseline_decodes(self):
        pixels = bytes([123]) * (REFERENCE_SIZE[0] * REFERENCE_SIZE[1])
        reference = decode_reference({
            "pixels_zlib_base64": base64.b64encode(
                zlib.compress(pixels, 9)
            ).decode("ascii")
        })

        self.assertEqual(reference.size, REFERENCE_SIZE)
        self.assertEqual(reference.mode, "L")
        self.assertEqual(reference.getpixel((0, 0)), 123)

    def test_overlay_keeps_actual_image_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = root / "actual.png"
            camera_path = root / "camera.json"
            goal = root / "goal.png"
            overlay = root / "overlay.png"

            Image.new("RGB", (240, 180), (120, 120, 120)).save(actual)
            camera_path.write_text(
                json.dumps({
                    "target": [0, 0, 5],
                    "yaw": 0.0,
                    "pitch": 0.0,
                    "roll": 0.0,
                    "distance": 80.0,
                    "fov": 0.0,
                }),
                encoding="utf-8",
            )

            render("simple-box", camera_path, actual, goal, overlay)

            result = Image.open(overlay).convert("RGB")
            self.assertEqual(result.getpixel((120, 90)), (120, 120, 120))


if __name__ == "__main__":
    unittest.main()
