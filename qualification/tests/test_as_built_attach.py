"""Qualification contract for attach(as_built=True)."""
import json
import os
from pathlib import Path
import unittest

from scpf.runner import run_script


ROOT = Path(__file__).resolve().parents[2]
NATIVE_ROOT = os.environ.get("SCPF_NATIVE_ROOT")


class AsBuiltAttachCommandTests(unittest.TestCase):
    def test_existing_child_pose_is_preserved_before_as_built_joint(self):
        document = run_script(
            ROOT / "examples/as-built-attach/scpf/model.py"
        )
        commands = document["commands"]

        components = [
            row["params"]["name"]
            for row in commands
            if row["command"] == "component.create"
        ]
        self.assertEqual(components, ["Base", "Marker"])

        moves = [
            row["params"]
            for row in commands
            if row["command"] == "occurrence.move"
            and row["params"]["occurrence"] == "Marker:1"
        ]
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["translate"], [50.0, 20.0, 15.0])
        self.assertEqual(moves[0]["axis"], [0.0, 0.0, 1.0])
        self.assertEqual(moves[0]["angle"], "90 deg")

        as_built = [
            row["params"]
            for row in commands
            if row["command"] == "joint.as_built"
        ]
        self.assertEqual(len(as_built), 1)
        self.assertEqual(
            as_built[0],
            {
                "type": "rigid",
                "name": "Attach Marker:1 to Base:1",
                "a": "Base:1",
                "b": "Marker:1",
            },
        )
        self.assertFalse(any(
            row["command"] == "joint.create"
            for row in commands
        ))


@unittest.skipUnless(NATIVE_ROOT, "native SolidCraft evidence not supplied")
class AsBuiltAttachNativeTests(unittest.TestCase):
    def test_native_as_built_joint_keeps_authored_pose(self):
        data = _load(
            Path(NATIVE_ROOT)
            / "as-built-attach"
            / "measurements.json"
        )
        self.assertEqual(data["body_count"], 2)
        self.assertEqual(
            _bbox(_body(data, "Base")),
            ([-20.0, -15.0, 0.0], [20.0, 15.0, 10.0]),
        )
        self.assertEqual(
            _bbox(_body(data, "Marker")),
            ([45.0, 5.0, 15.0], [55.0, 35.0, 23.0]),
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
