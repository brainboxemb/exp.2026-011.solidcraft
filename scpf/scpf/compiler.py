"""Compile SCPF model intent to native SolidCraft JSON command documents.

The compiler only describes operations. Native SolidCraft performs all
actual BRep booleans, sketches, fillets and geometric verification.
"""
from math import isfinite, hypot

from .core import (
    Shape, Parameter, command_value, number_text, parameters_in, value_of,
)


class ModelError(ValueError):
    """An unsupported or geometrically invalid CAD description."""


def _require_positive(value, label):
    num = value_of(value)
    if not isfinite(num) or num <= 0:
        raise ModelError(f"{label} must be positive")
    return num


def _command(command_name, **params):
    return {"command": command_name, "params": params}


def _param_commands(params):
    return [
        _command("parameters.add", name=p.name,
                 expression=number_text(p.value), unit="mm")
        for p in params
    ]


def _collect(node, values=None):
    """Collect named parameters in first-use order, rejecting conflicts."""
    if values is None:
        values = {}
    if isinstance(node, Shape):
        _collect(node.data, values)
    elif isinstance(node, (tuple, list)):
        for item in node:
            _collect(item, values)
    else:
        for param in parameters_in(node):
            previous = values.setdefault(param.name, param.value)
            if previous != param.value:
                raise ModelError(f"conflicting values for parameter {param.name}")
    return tuple(Parameter(k, v) for k, v in values.items())


def _half(dim, negative=False):
    if isinstance(dim, Parameter):
        return f"-{dim.name} / 2" if negative else f"{dim.name} / 2"
    return -value_of(dim) / 2 if negative else value_of(dim) / 2


def _cylinder_base(height, axis):
    if isinstance(height, Parameter):
        half = f"-({height.name}) / 2"
    elif hasattr(height, "expression"):
        half = f"-({height.expression}) / 2"
    else:
        half = -value_of(height) / 2
    return {
        "X": [half, 0, 0],
        "Y": [0, half, 0],
        "Z": [0, 0, half],
    }[axis]


def _shift(offset, delta):
    return tuple(a + b for a, b in zip(offset, delta))


def _add_offset(coord, offset):
    """Offset either a literal coordinate or a SolidCraft expression."""
    if not offset:
        return coord
    if isinstance(coord, str):
        return f"({coord}) + {number_text(offset)}"
    return coord + offset


def _csg_primitive(shape, body_name, operation, *, axis="Z", offset=(0, 0, 0), centered=False):
    kind, data = shape.kind, shape.data
    if kind == "cube":
        (size,) = data
        _require_positive(size, "cube size")
        params = dict(length=command_value(size), width=command_value(size),
                      height=command_value(size), center=list(offset),
                      operation=operation)
        command = "solid.box"
    elif kind == "sphere":
        (radius,) = data
        _require_positive(radius, "sphere radius")
        params = dict(radius=command_value(radius), center=list(offset),
                      operation=operation)
        command = "solid.sphere"
    elif kind == "cylinder3d":
        height, diameter = data
        _require_positive(height, "cylinder height")
        _require_positive(diameter, "cylinder diameter")
        base = _cylinder_base(height, axis) if centered else [0, 0, 0]
        params = dict(height=command_value(height),
                      diameter=command_value(diameter),
                      base=[_add_offset(coord, delta)
                            for coord, delta in zip(base, offset)],
                      axis=axis, operation=operation)
        command = "solid.cylinder"
    else:
        raise ModelError(f"not a supported CSG primitive: {kind}")

    if operation == "new":
        params["body_name"] = body_name
    else:
        params["targets"] = [body_name]
    return _command(command, **params)


def _csg_apply(shape, name, operation, offset=(0, 0, 0)):
    if shape.kind == "translated":
        child, delta = shape.data
        return _csg_apply(child, name, operation, _shift(offset, delta))
    if shape.kind in ("cube", "sphere", "cylinder3d"):
        return [_csg_primitive(shape, name, operation, offset=offset)]
    if shape.kind == "orient" and operation in ("cut", "join"):
        cylinder, axes = shape.data
        return [
            _csg_primitive(cylinder, name, operation, axis=axis, offset=offset, centered=True)
            for axis in axes
        ]
    if shape.kind == "union" and operation in ("cut", "join"):
        left, right = shape.data
        return _csg_apply(left, name, operation, offset) + _csg_apply(right, name, operation, offset)
    raise ModelError(f"unsupported CSG {operation}: {shape.kind}")


def _csg_new(shape, name, offset=(0, 0, 0)):
    if shape.kind == "placed3d":
        child, x, y, z = shape.data
        if child.kind != "cylinder3d":
            raise ModelError("Only Cylinder3D is supported by 3D placement")
        return _csg_new(child, name, (command_value(x), command_value(y), command_value(z)))
    if shape.kind == "translated":
        child, delta = shape.data
        return _csg_new(child, name, _shift(offset, delta))
    if shape.kind in ("cube", "sphere", "cylinder3d"):
        return [_csg_primitive(shape, name, "new", offset=offset)]
    if shape.kind == "intersection":
        left, right = shape.data
        return _csg_new(left, name, offset) + _csg_apply(right, name, "intersect", offset)
    if shape.kind == "difference":
        left, right = shape.data
        return _csg_new(left, name, offset) + _csg_apply(right, name, "cut", offset)
    if shape.kind == "union":
        left, right = shape.data
        return _csg_new(left, name, offset) + _csg_apply(right, name, "join", offset)
    raise ModelError(f"unsupported root CSG shape: {shape.kind}")


def _plate(shape, name):
    """Compile a filleted box minus Z-cylinder pattern as editable features."""
    if shape.kind != "difference":
        raise ModelError("feature CAD requires box - cylinder pattern")
    body, cutters = shape.data
    if body.kind != "fillet" or cutters.kind != "pattern":
        raise ModelError("feature CAD requires filleted box - cylinder pattern")
    box, fillet_radius, edges = body.data
    if box.kind != "box" or edges != "vertical":
        raise ModelError("only vertical fillets on an axis-aligned box are supported")
    length, width, thickness = box.data
    length_mm = _require_positive(length, "length")
    width_mm = _require_positive(width, "width")
    height_mm = _require_positive(thickness, "thickness")
    radius = _require_positive(fillet_radius, "fillet radius")
    if radius * 2 >= min(length_mm, width_mm):
        raise ModelError("fillet radius exceeds box width")

    cylinder, spacing_x, spacing_y = cutters.data
    if cylinder.kind != "cylinder3d":
        raise ModelError("pattern requires cylinders")
    cylinder_height, diameter = cylinder.data
    if _require_positive(cylinder_height, "cylinder height") < height_mm:
        raise ModelError("cylinder cutter does not pass through the plate")
    diameter_mm = _require_positive(diameter, "hole diameter")
    sx = _require_positive(spacing_x, "pattern X spacing")
    sy = _require_positive(spacing_y, "pattern Y spacing")
    hx, hy = sx / 2, sy / 2
    positions = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    for i, (x, y) in enumerate(positions):
        if abs(x) + diameter_mm / 2 >= length_mm / 2 or abs(y) + diameter_mm / 2 >= width_mm / 2:
            raise ModelError("a cylinder falls outside the plate")
        for a, b in positions[:i]:
            if hypot(x - a, y - b) <= diameter_mm:
                raise ModelError("cylinder cutters overlap")

    # The SolidCraft face selection uses the known pre-cut top face.
    # The cylinders are represented as native sketch circles and a cut feature,
    # retaining SolidCraft's editable history rather than exporting a mesh.
    steps = [
        _command("sketch.create", plane="XY", name=f"{name} footprint"),
        _command("sketch.rectangle.two_point",
                 p0=[_half(length, True), _half(width, True)],
                 p1=[_half(length), _half(width)]),
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(thickness), body_name=name),
        _command("solid.fillet",
                 edges=[
                     [-length_mm / 2, -width_mm / 2, height_mm / 2],
                     [length_mm / 2, -width_mm / 2, height_mm / 2],
                     [length_mm / 2, width_mm / 2, height_mm / 2],
                     [-length_mm / 2, width_mm / 2, height_mm / 2],
                 ], radius=value_of(fillet_radius), body=name),
        _command("sketch.create", plane={"face": [0, 0, height_mm]},
                 name=f"{name} top-face holes"),
    ]
    steps += [
        _command("sketch.circle.center", center=[x, y], diameter=diameter_mm)
        for x, y in positions
    ]
    steps += [
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(thickness),
                 direction="negative", operation="cut", targets=[name]),
    ]
    # Consistent with reviewed Rust fixture: pattern offsets are physical
    # dimensions, but the initial base dimensions remain named parameters.
    used = parameters_in(length, width, thickness)
    return _param_commands(used) + steps


def _has_profile(shape):
    if shape.kind == "polygon":
        return True
    if shape.kind in ("fillet", "extrusion", "holes"):
        return _has_profile(shape.data[0])
    return False


def _profile_features(shape, name):
    """Compile Polygon.extrude().fillet().holes() into native CAD history.

    Only one closed planar polygon, one extrusion, optional explicit edge
    fillet and an XY circle sketch are supported here. Coordinates are
    evaluated at the supplied parameter defaults; general parametric sketch
    constraints are intentionally not claimed.
    """
    holes = None
    if shape.kind == "holes":
        shape, positions, diameter, depth, plane = shape.data
        holes = (positions, diameter, depth, plane)

    fillet = None
    if shape.kind == "fillet":
        shape, radius, edges = shape.data
        if edges == "vertical":
            raise ModelError("polygon fillet requires explicit 3D edge points")
        fillet = (radius, edges)

    if shape.kind != "extrusion":
        raise ModelError("profile features require a Polygon extrusion")
    polygon, distance, direction = shape.data
    if polygon.kind != "polygon":
        raise ModelError("extrude() requires a Polygon")
    points, sketch_plane = polygon.data
    _require_positive(distance, "extrusion distance")
    if direction not in ("positive", "negative"):
        raise ModelError("invalid extrusion direction")

    # Closed sketch uses real coordinates; SolidCraft may later support
    # symbolic point constraints, but this is not established here.
    concrete_points = []
    for point in points:
        coords = [value_of(v) for v in point]
        if not all(isfinite(x) for x in coords):
            raise ModelError("non-finite polygon coordinate")
        concrete_points.append(coords)

    # Avoid silently introducing invalid zero-length sketch edges.
    if len(set(tuple(x) for x in concrete_points)) != len(concrete_points):
        raise ModelError("duplicate polygon vertices")
    for p, q in zip(concrete_points, concrete_points[1:] + concrete_points[:1]):
        if p == q:
            raise ModelError("zero-length polygon edge")

    steps = [
        _command("sketch.create", plane=sketch_plane, name="Profile"),
        _command("sketch.line", points=concrete_points, closed=True,
                 ids=[chr(ord("a") + i) for i in range(len(points))]),
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(distance),
                 direction=direction, body_name=name),
    ]
    if fillet is not None:
        radius, edges = fillet
        _require_positive(radius, "fillet radius")
        locations = []
        for point in edges:
            coords = [value_of(x) for x in point]
            if not all(isfinite(x) for x in coords):
                raise ModelError("non-finite edge selection")
            locations.append(coords)
        steps.append(_command("solid.fillet", edges=locations,
                              radius=value_of(radius)))

    if holes is not None:
        positions, diameter, depth, plane = holes
        _require_positive(diameter, "hole diameter")
        _require_positive(depth, "hole cut depth")
        if plane != "XY":
            raise ModelError("only XY hole sketches are supported")
        steps.append(_command("sketch.create", plane=plane, name="Holes"))
        for point in positions:
            coords = [value_of(x) for x in point]
            if not all(isfinite(x) for x in coords):
                raise ModelError("non-finite hole centre")
            steps.append(_command("sketch.circle.center",
                                  center=coords, diameter=value_of(diameter)))
        # SolidCraft's XZ sketch coordinate v maps to NEGATIVE world Z.
        # The source Bracket profile uses local v=0..30 and therefore has
        # world Z=-30..0. An XY sketch at world Z=0 must cut towards -Z.
        # Do not infer the direction directly from unsigned sketch values.
        if sketch_plane != "XZ":
            raise ModelError("automatic XY hole direction requires XZ profile")
        local_vertical = [point[1] for point in concrete_points]
        world_z = [-v for v in local_vertical]
        low, high = min(world_z), max(world_z)
        if high <= 0 and low < 0:
            hole_direction = "negative"
        elif low >= 0 and high > 0:
            hole_direction = "positive"
        else:
            raise ModelError("XY sketch crosses solid on both sides; choose a face-based cutter")
        steps.extend([
            _command("sketch.finish"),
            _command("solid.extrude", distance=command_value(depth),
                     direction=hole_direction, operation="cut"),
        ])
    return _param_commands(_collect((distance, shape))) + steps


def compile_model(shape: Shape, name: str) -> dict:
    """Return a native SolidCraft JSON document for a supported SCPF Shape."""
    if not isinstance(shape, Shape):
        raise TypeError("the final script expression must produce a Shape")
    if not name or not name.isidentifier():
        raise ModelError("the model name must be a valid identifier")
    from .sketch_features import _is_rectangular_feature, compile_sketch_features
    if _is_rectangular_feature(shape):
        commands = compile_sketch_features(shape, name)
    elif shape.kind in ("holes", "extrusion", "fillet") and _has_profile(shape):
        commands = _profile_features(shape, name)
    elif shape.kind == "difference" and shape.data[0].kind == "fillet":
        commands = _plate(shape, name)
    else:
        commands = _param_commands(_collect(shape)) + _csg_new(shape, name)
    return {"commands": commands}
