#!/usr/bin/env python3
"""Build deterministic orthographic cameras from SolidCraft measurement JSON."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


VIEWS = {
    "front": (0.0, 0.0),
    "right": (-math.pi / 2.0, 0.0),
    "top": (0.0, math.pi / 2.0),
    "iso": (-math.pi / 4.0, math.radians(32.0)),
}


def model_bounds(data: dict) -> tuple[list[float], list[float]]:
    bodies = data.get("bodies", [])
    if not bodies:
        raise ValueError("measurement JSON contains no bodies")
    mins = [
        min(float(body["bbox"]["min"][axis]) for body in bodies)
        for axis in range(3)
    ]
    maxs = [
        max(float(body["bbox"]["max"][axis]) for body in bodies)
        for axis in range(3)
    ]
    return mins, maxs


def camera(data: dict, view: str) -> dict:
    if view not in VIEWS:
        raise ValueError(f"unknown view: {view}")
    mins, maxs = model_bounds(data)
    target = [(lo + hi) / 2.0 for lo, hi in zip(mins, maxs)]
    spans = [hi - lo for lo, hi in zip(mins, maxs)]
    size = max(max(spans), 1.0)

    # Orthographic SolidCraft view height is 0.8 * distance. Keep generous,
    # deterministic framing so baseline and mutated models are comparable.
    distance = size * 1.65
    yaw, pitch = VIEWS[view]
    return {
        "target": target,
        "yaw": yaw,
        "pitch": pitch,
        "roll": 0.0,
        "distance": distance,
        "fov": 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("measurements", type=Path)
    parser.add_argument("view", choices=sorted(VIEWS))
    args = parser.parse_args()
    data = json.loads(args.measurements.read_text(encoding="utf-8"))
    print(json.dumps(camera(data, args.view), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
