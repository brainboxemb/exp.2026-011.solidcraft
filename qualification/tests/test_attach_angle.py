"""Qualification contract for native attachment angle."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class AttachAngleCommandTests(unittest.TestCase):
    def test_quarter_turn_is_emitted_on_rigid_joint(self):
        document = run_script(
            ROOT / "examples/attach-angle/scpf/model.py"
        )
        joints = [
            row["params"]
            for row in document["commands"]
            if row["command"] == "joint.create"
        ]
        self.assertEqual(len(joints), 1)
        self.assertEqual(joints[0]["type"], "rigid")
        self.assertEqual(joints[0]["angle"], 90)
        self.assertEqual(joints[0]["a"]["occurrence"], "Base:1")
        self.assertEqual(joints[0]["b"]["occurrence"], "Arm:1")


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class AttachAngleNativeTests(unittest.TestCase):
    def test_native_quarter_turn_swaps_arm_footprint_axes(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "attach-angle"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 2)
        self.assertEqual(
            _bbox(_body(data, "Base")),
            ([-30.0, -30.0, 0.0], [30.0, 30.0, 10.0]),
        )
        self.assertEqual(
            _bbox(_body(data, "Arm")),
            ([-5.0, -15.0, 10.0], [5.0, 15.0, 16.0]),
        )


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _body(data, prefix):
    return next(
        body for body in data["bodies"]
        if body["name"].startswith(prefix)
    )


def _bbox(body):
    return (
        [round(value, 6) for value in body["bbox"]["min"]],
        [round(value, 6) for value in body["bbox"]["max"]],
    )


if __name__ == "__main__":
    unittest.main()
