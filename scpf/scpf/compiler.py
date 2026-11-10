"""Compile SCPF model intent to native SolidCraft JSON command documents.

The compiler only describes operations. Native SolidCraft performs all
actual BRep booleans, sketches, fillets and geometric verification.
"""
from math import isfinite, hypot

from .core import (
    Shape, Parameter, Edges, command_value, number_text, parameters_in, value_of,
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


def compile_model(shape: Shape, name: str) -> dict:
    """Dispatch on the kind of CAD geometry, never on example/model names."""
    if not isinstance(shape, Shape):
        raise TypeError("the final script expression must produce a Shape")
    if not name or not name.isidentifier():
        raise ModelError("the model name must be a valid identifier")

    from .sketch_features import _is_rectangular_feature, compile_sketch_features
    from .polygon_features import _has_profile, compile_polygon_features
    from .box_features import _is_box_feature, compile_box_features
    from .csg import _csg_new

    if _is_rectangular_feature(shape):
        commands = compile_sketch_features(shape, name)
    elif _is_box_feature(shape):
        commands = compile_box_features(shape, name)
    elif _has_profile(shape):
        commands = compile_polygon_features(shape, name)
    else:
        commands = _param_commands(_collect(shape)) + _csg_new(shape, name)
    return {"commands": commands}
