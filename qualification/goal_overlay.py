#!/usr/bin/env python3
"""Render expected qualification geometry and overlays for fixed camera views."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qualification.expectations import EXPECTED_BOUNDS


BOX_EDGES = (
    (0, 1), (1, 3), (3, 2), (2, 0),
    (4, 5), (5, 7), (7, 6), (6, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
)


def _sub(a, b):
    return tuple(float(a[i]) - float(b[i]) for i in range(3))


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(v):
    length = math.sqrt(_dot(v, v))
    if length <= 0:
        raise ValueError("zero-length camera vector")
    return tuple(value / length for value in v)


def _camera_basis(camera):
    yaw = float(camera["yaw"])
    pitch = float(camera["pitch"])
    forward = (
        math.sin(yaw) * math.cos(pitch),
        math.cos(yaw) * math.cos(pitch),
        -math.sin(pitch),
    )
    world_up = (0.0, 0.0, 1.0)
    right = _norm(_cross(forward, world_up))
    up = _norm(_cross(right, forward))
    return right, up


def _project(point, camera, width, height):
    target = tuple(float(v) for v in camera["target"])
    right, up = _camera_basis(camera)
    delta = _sub(point, target)

    half_height = 0.4 * float(camera["distance"])
    half_width = half_height * (float(width) / float(height))
    if half_width <= 0 or half_height <= 0:
        raise ValueError("invalid orthographic camera size")

    x = width / 2.0 + _dot(delta, right) / half_width * width / 2.0
    y = height / 2.0 - _dot(delta, up) / half_height * height / 2.0
    return (x, y)


def _corners(bounds):
    lo = bounds["min"]
    hi = bounds["max"]
    return [
        (lo[0], lo[1], lo[2]),
        (hi[0], lo[1], lo[2]),
        (lo[0], hi[1], lo[2]),
        (hi[0], hi[1], lo[2]),
        (lo[0], lo[1], hi[2]),
        (hi[0], lo[1], hi[2]),
        (lo[0], hi[1], hi[2]),
        (hi[0], hi[1], hi[2]),
    ]


def _draw_expected(image, camera, expected, *, labels=True):
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    font = ImageFont.load_default()

    for index, body in enumerate(expected):
        points = [_project(point, camera, width, height) for point in _corners(body)]
        # Alternate two strong line styles so neighbouring expected boxes remain
        # distinguishable without relying on the current SolidCraft body colours.
        line = (20, 110, 235, 230) if index % 2 == 0 else (0, 155, 110, 230)
        fill = (20, 110, 235, 18) if index % 2 == 0 else (0, 155, 110, 18)

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        draw.rectangle((min(xs), min(ys), max(xs), max(ys)), fill=fill)

        for a, b in BOX_EDGES:
            draw.line((points[a], points[b]), fill=line, width=3)

        if labels:
            center3d = tuple(
                (float(body["min"][axis]) + float(body["max"][axis])) / 2.0
                for axis in range(3)
            )
            x, y = _project(center3d, camera, width, height)
            label = str(body["label"])
            box = draw.textbbox((x + 5, y + 5), label, font=font)
            draw.rectangle(
                (box[0] - 3, box[1] - 2, box[2] + 3, box[3] + 2),
                fill=(255, 255, 255, 220),
            )
            draw.text((x + 5, y + 5), label, font=font, fill=(20, 35, 55, 255))

    return image


def render(case, camera_path, actual_path, goal_path, overlay_path):
    if case not in EXPECTED_BOUNDS:
        raise ValueError(f"no expected bounds declared for {case}")

    camera = json.loads(camera_path.read_text(encoding="utf-8"))
    actual = Image.open(actual_path).convert("RGBA")

    goal = Image.new("RGBA", actual.size, (248, 250, 253, 255))
    _draw_expected(goal, camera, EXPECTED_BOUNDS[case])
    goal.convert("RGB").save(goal_path)

    overlay = actual.copy()
    _draw_expected(overlay, camera, EXPECTED_BOUNDS[case])
    overlay.convert("RGB").save(overlay_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--camera", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--goal", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    args = parser.parse_args()

    render(args.case, args.camera, args.actual, args.goal, args.overlay)
    print(f"Wrote goal and overlay for {args.case}: {args.actual.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
