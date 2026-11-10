"""Compile SCPF model intent to native SolidCraft JSON command documents.

The compiler only describes operations. Native SolidCraft performs all
actual BRep booleans, sketches, fillets and geometric verification.
"""
from math import isfinite

from .core import (
    Shape, Parameter, number_text, parameters_in, value_of,
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
    """Compile a shape tree by operation semantics, not example names."""
    if not isinstance(shape, Shape):
        raise TypeError("the final script expression must produce a Shape")
    if not name or not name.isidentifier():
        raise ModelError("the model name must be a valid identifier")
    from .features import _is_feature_tree, compile_features
    from .csg import _csg_new
    commands = (compile_features(shape, name) if _is_feature_tree(shape)
                else _param_commands(_collect(shape)) + _csg_new(shape, name))
    return {"commands": commands}
