"""CSG primitive translation to native SolidCraft commands.

This module is not a geometry engine. SolidCraft executes these operations.
"""
from .core import Shape, Parameter, Expression, pv, command_value, number_text
from .compiler import ModelError, _command, _require_positive

def _half(dim, negative=False):
    if isinstance(dim, Parameter):
        return f"-{dim.name} / 2" if negative else f"{dim.name} / 2"
    if isinstance(dim, Expression):
        expression = command_value(dim)
        return f"-({expression}) / 2" if negative else f"({expression}) / 2"
    return -pv(dim) / 2 if negative else pv(dim) / 2


def _cylinder_base(height, axis):
    if isinstance(height, Parameter):
        half = f"-({height.name}) / 2"
    elif hasattr(height, "expression"):
        half = f"-({height.expression}) / 2"
    else:
        half = -pv(height) / 2
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
    if kind == "box":
        length, width, height = data
        _require_positive(length, "box length")
        _require_positive(width, "box width")
        _require_positive(height, "box height")
        params = dict(length=command_value(length), width=command_value(width),
                      height=command_value(height), center=list(offset),
                      operation=operation)
        command = "solid.box"
    elif kind == "sphere":
        (radius,) = data
        _require_positive(radius, "sphere radius")
        params = dict(radius=command_value(radius), center=list(offset),
                      operation=operation)
        command = "solid.sphere"
    elif kind == "cylinder":
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
    if shape.kind in ("box", "sphere", "cylinder"):
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
        if child.kind != "cylinder":
            raise ModelError("Only Cylinder is supported by 3D placement")
        return _csg_new(child, name, (command_value(x), command_value(y), command_value(z)))
    if shape.kind == "translated":
        child, delta = shape.data
        return _csg_new(child, name, _shift(offset, delta))
    if shape.kind in ("box", "sphere", "cylinder"):
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


