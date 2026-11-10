#!/usr/bin/env python3
"""Measure a binary or ASCII STL using only the Python standard library."""

import json
import math
import struct
import sys
from pathlib import Path


def triangles(path: Path):
    data = path.read_bytes()
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if len(data) == 84 + count * 50:
            for i in range(count):
                off = 84 + i * 50 + 12
                coords = struct.unpack_from("<9f", data, off)
                yield tuple(coords[0:3]), tuple(coords[3:6]), tuple(coords[6:9])
            return

    verts = []
    for line in data.decode("utf-8", errors="strict").splitlines():
        fields = line.strip().split()
        if len(fields) == 4 and fields[0].lower() == "vertex":
            verts.append(tuple(map(float, fields[1:])))
            if len(verts) == 3:
                yield tuple(verts)
                verts.clear()


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


path = Path(sys.argv[1])
tris = list(triangles(path))
if not tris:
    raise SystemExit(f"no triangles in {path}")

points = [p for tri in tris for p in tri]
bbox_min = [min(p[i] for p in points) for i in range(3)]
bbox_max = [max(p[i] for p in points) for i in range(3)]

area = 0.0
signed_volume = 0.0
for a, b, c in tris:
    cr = cross(sub(b, a), sub(c, a))
    area += 0.5 * math.sqrt(dot(cr, cr))
    signed_volume += dot(a, cross(b, c)) / 6.0

result = {
    "file": str(path),
    "triangles": len(tris),
    "bbox": {"min": bbox_min, "max": bbox_max},
    "surface_area_mm2": area,
    "volume_mm3": abs(signed_volume),
}
print(json.dumps(result, indent=2))
