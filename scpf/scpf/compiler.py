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


def _command(name, **params):
    return {"command": name, "params": params}


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


def _csg_primitive(shape, body_name, operation, *, axis="Z"):
    kind, data = shape.kind, shape.data
    if kind == "cube":
        (size,) = data
        _require_positive(size, "cube size")
        params = dict(length=command_value(size), width=command_value(size),
                      height=command_value(size), center=[0, 0, 0],
                      operation=operation)
        command = "solid.box"
    elif kind == "sphere":
        (radius,) = data
        _require_positive(radius, "sphere radius")
        params = dict(radius=command_value(radius), center=[0, 0, 0],
                      operation=operation)
        command = "solid.sphere"
    elif kind == "cylinder":
        height, diameter = data
        _require_positive(height, "cylinder height")
        _require_positive(diameter, "cylinder diameter")
        params = dict(height=command_value(height),
                      diameter=command_value(diameter),
                      base=_cylinder_base(height, axis), axis=axis,
                      operation=operation)
        command = "solid.cylinder"
    else:
        raise ModelError(f"not a supported CSG primitive: {kind}")

    if operation == "new":
        params["body_name"] = body_name
    else:
        params["targets"] = [body_name]
    return _command(command, **params)


def _csg_apply(shape, name, operation):
    if shape.kind in ("cube", "sphere", "cylinder"):
        return [_csg_primitive(shape, name, operation)]
    if shape.kind == "orient" and operation in ("cut", "join"):
        cylinder, axes = shape.data
        return [
            _csg_primitive(cylinder, name, operation, axis=axis)
            for axis in axes
        ]
    if shape.kind == "union" and operation in ("cut", "join"):
        left, right = shape.data
        return _csg_apply(left, name, operation) + _csg_apply(right, name, operation)
    raise ModelError(f"unsupported CSG {operation}: {shape.kind}")


def _csg_new(shape, name):
    if shape.kind in ("cube", "sphere", "cylinder"):
        return [_csg_primitive(shape, name, "new")]
    if shape.kind == "intersection":
        left, right = shape.data
        return _csg_new(left, name) + _csg_apply(right, name, "intersect")
    if shape.kind == "difference":
        left, right = shape.data
        return _csg_new(left, name) + _csg_apply(right, name, "cut")
    if shape.kind == "union":
        left, right = shape.data
        return _csg_new(left, name) + _csg_apply(right, name, "join")
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
    if cylinder.kind != "cylinder":
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


def compile_model(shape: Shape, name: str) -> dict:
    """Return a native SolidCraft JSON document for a supported SCPF Shape."""
    if not isinstance(shape, Shape):
        raise TypeError("the final script expression must produce a Shape")
    if not name or not name.isidentifier():
        raise ModelError("the model name must be a valid identifier")
    if shape.kind == "difference" and shape.data[0].kind == "fillet":
        commands = _plate(shape, name)
    else:
        commands = _param_commands(_collect(shape)) + _csg_new(shape, name)
    return {"commands": commands}
