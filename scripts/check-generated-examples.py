#!/usr/bin/env python3
"""Gate publication to generated-examples on complete five-way CAD evidence.

Run this on a staging directory containing results collected from the
comparison workflows, not on the source tree. The gate checks presence and
basic validity, and intentionally does NOT publish anything by itself.
"""
import argparse
import json
from pathlib import Path

IMPLEMENTATIONS = ("scrf", "cadquery", "microcad", "vcad", "pythonscad")
EXAMPLES = ("plate", "csg-cube")


def qualify(root: Path) -> list[str]:
    problems = []
    for example in EXAMPLES:
        for implementation in IMPLEMENTATIONS:
            directory = root / example / implementation
            if not directory.is_dir():
                problems.append(f"{example}/{implementation}: missing directory")
                continue
            measurements = directory / "measurements.json"
            if not measurements.is_file():
                problems.append(f"{example}/{implementation}: missing measurements.json")
                continue
            try:
                data = json.loads(measurements.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                problems.append(f"{example}/{implementation}: invalid measurements: {exc}")
                continue
            if not isinstance(data, dict):
                problems.append(f"{example}/{implementation}: measurements are not an object")
                continue
            # The native SolidCraft evaluation uses total.volume_mm3;
            # other CAD engines currently use volume_mm3 at top level.
            volume = data.get("volume_mm3", data.get("total", {}).get("volume_mm3"))
            if not isinstance(volume, (int, float)) or isinstance(volume, bool):
                problems.append(f"{example}/{implementation}: missing numeric volume")
                continue
            limits = (57500, 58400) if example == "plate" else (34000, 39000)
            if not limits[0] < volume < limits[1]:
                problems.append(f"{example}/{implementation}: volume {volume} outside {limits}")
            formats = {p.suffix.lower() for p in directory.iterdir() if p.is_file() and p.stat().st_size > 0}
            if not formats.intersection({".stl", ".step", ".sc"}):
                problems.append(f"{example}/{implementation}: missing non-empty CAD export")
            if implementation == "scrf" and ".sc" not in formats:
                problems.append(f"{example}/{implementation}: missing native SolidCraft .sc")
            if implementation == "vcad" and example == "csg-cube":
                # Mesh-only is legitimate for the pinned kernel, but it must
                # be documented rather than silently passing as exact BRep.
                if "why_not_brep" not in data:
                    problems.append("csg-cube/vcad: missing BRep degradation diagnostic")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="staging root: plate/* and csg-cube/*")
    args = parser.parse_args()
    problems = qualify(args.directory)
    if problems:
        print("NOT READY for generated-examples publication:")
        for issue in problems:
            print(f" - {issue}")
        return 1
    print("Five implementations × two examples: baseline evidence gate passed.")
    print("Review preview images and geometry before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
