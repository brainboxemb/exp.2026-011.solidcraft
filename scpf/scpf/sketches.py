"""Native SolidCraft sketch construction for primitive CAD profiles.

Each supported base shape returns its command list plus simple shape metadata.
Feature operations (Hole, Fillet, join, cut) are handled separately.
"""
from math import isfinite
from .core import Shape, Parameter, command_value, value_of
from .compiler import ModelError, _command, _require_positive
from .csg import _half

def _circle_profiles(shape, dx=0, dy=0, z=0):
    """Return circles from planar shapes and their placements.

    Each circle is (x, y, z, diameter). A union in a 2D sketch is a
    collection of profiles, not a 3D Boolean operation.
    """
    if shape.kind == "positioned":
        base, x, y, dz = shape.data
        if base.kind == "positioned":
            raise ValueError("nested at() placement is not yet supported")
        return _circle_profiles(base, value_of(x), value_of(y), dz)
    if shape.kind == "circle":
        (diameter,) = shape.data
        return [(dx, dy, z, diameter)]
    if shape.kind == "union":
        left, right = shape.data
        return _circle_profiles(left) + _circle_profiles(right)
    raise ValueError("Expected Circle or union of Circle profiles")


def _rectangle_profile(shape):
    if shape.kind == "rectangle":
        return shape.data, (0, 0, 0)
    if shape.kind == "positioned":
        child, x, y, z = shape.data
        if child.kind != "rectangle":
            raise ValueError("Unsupported positioned profile")
        return child.data, (x, y, z)
    raise ValueError("Base shape must be a Rectangle")



def compile_base(shape, name):
    """Create a native editable base body, regardless of example/model name."""
    if shape.kind == "box":
        length, width, height = shape.data
        _require_positive(length, "box length")
        _require_positive(width, "box width")
        _require_positive(height, "box height")
        steps = [
            _command("sketch.create", plane="XY", name=f"{name} footprint"),
            _command("sketch.rectangle.two_point",
                     p0=[_half(length, True), _half(width, True)],
                     p1=[_half(length), _half(width)]),
            _command("sketch.finish"),
            _command("solid.extrude", distance=command_value(height),
                     body_name=name),
        ]
        return steps, {"profile": "rectangle", "width": length,
                       "depth": width, "thickness": height,
                       "origin": (-length / 2, -width / 2, 0)}

    if shape.kind == "tapered_box":
        # A straight front mask and a long, smoothly tapered rear housing.
        # The two section sketches are left in the native model history.
        original, start, inset = shape.data
        width, height, depth = original.data
        _require_positive(width, "taper width")
        _require_positive(height, "taper height")
        _require_positive(depth, "taper depth")
        if not 0 < value_of(start) < value_of(depth):
            raise ModelError("taper start lies outside the box")
        if not 0 < 2 * value_of(inset) < min(value_of(width), value_of(height)):
            raise ModelError("taper inset is too large")

        x0, x1 = _half(width, True), _half(width)
        y0, y1 = _half(height, True), _half(height)

        def shifted(edge, inward):
            offset = command_value(inset)
            if isinstance(edge, str) or isinstance(offset, str):
                return f"({edge}) {'+' if inward else '-'} ({offset})"
            return edge + offset if inward else edge - offset

        front = f"{name} footprint"
        rear_start = f"{name} rear start"
        rear_end = f"{name} rear perimeter"

        def sketch_rectangle(sketch_name, offset, a, b):
            plane = dict(plane="XY", name=sketch_name)
            if offset is not None:
                plane["offset"] = command_value(offset)
            return [
                _command("sketch.create", **plane),
                _command("sketch.rectangle.two_point", p0=a, p1=b),
                _command("sketch.finish"),
            ]

        steps = sketch_rectangle(front, None, [x0, y0], [x1, y1])
        steps.append(_command(
            "solid.extrude", distance=command_value(start), body_name=name,
        ))
        steps.extend(sketch_rectangle(
            rear_start, start, [x0, y0], [x1, y1],
        ))
        steps.extend(sketch_rectangle(
            rear_end, depth,
            [shifted(x0, True), shifted(y0, True)],
            [shifted(x1, False), shifted(y1, False)],
        ))
        steps.append(_command(
            "solid.loft",
            sections=[{"sketch": rear_start}, {"sketch": rear_end}],
            operation="join", targets=[name],
        ))
        return steps, {
            "profile": "rectangle", "width": width, "depth": height,
            "thickness": depth,
            "origin": (-value_of(width) / 2, -value_of(height) / 2, 0),
        }

    if shape.kind != "extrusion":
        raise ModelError(f"Expected a solid base, got {shape.kind}")
    profile, distance, direction = shape.data
    if direction not in ("positive", "negative", "symmetric"):
        raise ModelError("extrusion direction must be positive, negative or symmetric")
    _require_positive(distance, "extrusion distance")

    if profile.kind in ("rectangle", "positioned"):
        try:
            (width, depth), (x, y, z) = _rectangle_profile(profile)
        except ValueError:
            pass
        else:
            _require_positive(width, "rectangle width")
            _require_positive(depth, "rectangle depth")
            plane = {"plane": "XY", "name": "Base"}
            if value_of(z) != 0 or isinstance(z, Parameter):
                plane["offset"] = command_value(z)
            return [
                _command("sketch.create", **plane),
                _command("sketch.rectangle.two_point",
                         p0=[command_value(x), command_value(y)],
                         p1=[command_value(width), command_value(depth)]),
                _command("sketch.finish"),
                _command("solid.extrude", distance=command_value(distance),
                         direction=direction, body_name=name),
            ], {"profile": "rectangle", "width": width, "depth": depth,
                "thickness": distance, "origin": (x, y, z)}

    if profile.kind == "polygon":
        points, plane, segment_ids = profile.data
        concrete = [tuple(value_of(v) for v in point) for point in points]
        if not all(isfinite(v) for point in concrete for v in point):
            raise ModelError("non-finite polygon coordinate")
        if len(set(concrete)) != len(concrete):
            raise ModelError("duplicate polygon vertices")
        if any(a == b for a, b in zip(concrete, concrete[1:] + concrete[:1])):
            raise ModelError("zero-length polygon edge")
        # Preserve existing (non-symmetric) SCPF JSON fixtures.
        # Symmetric bracket extrusions need named coordinates so their
        # profile continues to follow editable native CAD parameters.
        symbolic = (
            [[command_value(v) for v in point] for point in points]
            if direction == "symmetric" else [list(p) for p in concrete]
        )
        return [
            _command("sketch.create", plane=plane, name="Profile"),
            _command("sketch.line",
                     points=symbolic, closed=True,
                     ids=list(segment_ids) if segment_ids is not None else
                         [chr(ord("a") + i) for i in range(len(points))]),
            _command("sketch.finish"),
            _command("solid.extrude", distance=command_value(distance),
                     direction=direction, body_name=name),
        ], {"profile": "polygon", "sketch_plane": plane,
            "thickness": distance, "extrusion_direction": direction,
            "profile_points": points, "profile_ids": segment_ids}

    if profile.kind in ("circle", "positioned"):
        try:
            circles = _circle_profiles(profile)
        except ValueError:
            pass
        else:
            if len(circles) != 1:
                raise ModelError("a standalone circular base needs one circle")
            x, y, z, diameter = circles[0]
            _require_positive(diameter, "circle diameter")
            plane = {"plane": "XY", "name": "Profile"}
            if value_of(z):
                plane["offset"] = command_value(z)
            return [
                _command("sketch.create", **plane),
                _command("sketch.circle.center",
                         center=[command_value(x), command_value(y)],
                         diameter=command_value(diameter)),
                _command("sketch.finish"),
                _command("solid.extrude", distance=command_value(distance),
                         direction=direction, body_name=name),
            ], {"profile": "circle", "thickness": distance}

    raise ModelError("base extrusion requires Rectangle2D, Circle2D or Polygon2D")
