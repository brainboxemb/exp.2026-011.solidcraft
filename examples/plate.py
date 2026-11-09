"""Minimal, repeatable SolidCraft Python example.

The same CAD commands drive a visible GUI (control port) or a headless MCP
session. No third-party module is imported until the real transport is used,
so the command sequence can be unit-tested offline.
"""

import argparse
import os
from pathlib import Path
from typing import Any


def construct_plate(cad: Any, *, length: float = 100, width: float = 60,
                    thickness: float = 10, hole_diameter: float = 20) -> None:
    """Make a centered rectangular plate with one through-hole (all mm)."""
    if min(length, width, thickness, hole_diameter) <= 0:
        raise ValueError("dimensions and hole diameter must be positive")
    if hole_diameter >= min(length, width):
        raise ValueError("the hole must fit inside the plate")

    cad.sketch.create(plane="XY", name="Plate")
    outline = cad.sketch.rectangle_center(
        center=(0, 0), corner=(length / 2, width / 2)
    )
    cad.sketch.circle_center(center=(0, 0), diameter=hole_diameter)
    cad.sketch.finish()
    if not isinstance(outline, dict) or "curves" not in outline:
        raise RuntimeError("SolidCraft did not return the outline curve IDs")
    cad.solid.extrude(
        distance=thickness,
        profiles=[{"curves": outline["curves"]}],
        body_name="Plate",
    )


def export_plate(target: str, destination: Path) -> Path:
    """Model via headless MCP or a GUI port and write a STEP export."""
    # scraftpybind's 0.2.0 ControlTransport defaults to the Linux directory.
    # SolidCraft stores GUI token files elsewhere on Windows; do not copy the
    # token or override an explicit setting from the user.
    if os.name == "nt" and "SOLIDCRAFT_CONTROL_DIR" not in os.environ:
        local = os.environ.get("LOCALAPPDATA")
        if local:
            os.environ["SOLIDCRAFT_CONTROL_DIR"] = str(Path(local) / "SolidCraft" / "control")

    from scraftcnc.pybind.scraftpybind import PyBind, connect

    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with connect(target) as transport:
        cad = PyBind(transport)
        construct_plate(cad)
        cad.file.export(path=str(destination))
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="headless",
                        help="'headless', GUI port 8080, or '0' for auto-discovery")
    parser.add_argument("--out", type=Path, default=Path("output/plate.step"))
    args = parser.parse_args()
    path = export_plate(args.target, args.out)
    print(f"Export request completed: {path}")


if __name__ == "__main__":
    main()
