"""Use Python as a small SolidCraft script language, without Python bindings.

SolidCraft itself accepts JSON commands. Python can assemble these commands and
pass them to the native CLI, with no third-party packages or protocol client.

From the experiment repository:
    python examples/python_cli_script.py              # write JSON only
    python examples/python_cli_script.py --run        # also export STEP

This is a source-level fixture, not yet verified against installed SolidCraft.
"""
import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def bracket_commands(*, arm_x: float = 40, arm_z: float = 30,
                     wall: float = 6, width: float = 60) -> dict[str, Any]:
    """Describe a simple L cross-section extruded to the given width in mm."""
    if min(arm_x, arm_z, wall, width) <= 0:
        raise ValueError("all dimensions must be positive")
    if wall >= min(arm_x, arm_z):
        raise ValueError("the wall must be smaller than both arms")
    points = [
        [0, 0], [arm_x, 0], [arm_x, wall],
        [wall, wall], [wall, arm_z], [0, arm_z],
    ]
    return {"commands": [
        {"command": "parameters.change",
         "params": {"name": "width", "expression": f"{width} mm"}},
        {"command": "sketch.create",
         "params": {"plane": "XZ", "name": "L profile"}},
        {"command": "sketch.line",
         "params": {"points": points, "closed": True}},
        {"command": "sketch.finish", "params": {}},
        {"command": "solid.extrude",
         "params": {"distance": "width", "direction": "negative",
                    "body_name": "Bracket"}},
    ]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm-x", type=float, default=40)
    parser.add_argument("--arm-z", type=float, default=30)
    parser.add_argument("--wall", type=float, default=6)
    parser.add_argument("--width", type=float, default=60)
    parser.add_argument("--script", type=Path,
                        default=Path("output/bracket.json"))
    parser.add_argument("--out", type=Path,
                        default=Path("output/bracket.step"))
    parser.add_argument("--run", action="store_true",
                        help="run generated script with SolidCraft CLI")
    args = parser.parse_args()

    script = bracket_commands(arm_x=args.arm_x, arm_z=args.arm_z,
                              wall=args.wall, width=args.width)
    script_path = args.script.resolve()
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        json.dumps(script, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {script_path}")

    if args.run:
        out_path = args.out.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["solidcraft-cli", "run", str(script_path), "--out", str(out_path)],
            check=True,
        )
        print(f"Requested STEP export to {out_path}")


if __name__ == "__main__":
    main()
