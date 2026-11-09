"""Small Python/SolidCraft transport fixture: a plate with one through hole.

Needs scraftcnc under PYTHONPATH and an appropriate SolidCraft runtime.
This fixture has not yet been verified against SolidCraft 0.30.1.
"""

import argparse
from pathlib import Path

from scraftcnc.pybind.scraftpybind import PyBind, connect


def build_plate(target: str, destination: Path) -> None:
    """Create 100 x 60 x 10 mm plate with a central 20 mm through-hole."""
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with connect(target) as transport:
        cad = PyBind(transport)
        cad.sketch.create(plane="XY", name="Plate")
        outline = cad.sketch.rectangle_center(center=(0, 0), corner=(50, 30))
        cad.sketch.circle_center(center=(0, 0), diameter=20)
        cad.sketch.finish()
        cad.solid.extrude(
            distance=10,
            profiles=[{"curves": outline["curves"]}],
            body_name="Plate",
        )
        cad.file.export(path=str(destination))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="headless", help="headless or GUI control port (e.g. 8080)")
    parser.add_argument("--out", type=Path, default=Path("output/plate.step"))
    args = parser.parse_args()
    build_plate(args.target, args.out)
    print(f"Exported {args.out.resolve()}")


if __name__ == "__main__":
    main()
