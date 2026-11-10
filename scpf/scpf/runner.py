"""Execute a trusted SCPF script, then compile its final model expression.

Scripts end with a function call (Plate()) or a dataclass design instance
(Bracket()). SCPF automatically calls build() on a design instance.
Within the model's build() or final function, a last geometry expression
acts as an implicit return. No show() or main() is required.
"""
import ast
from dataclasses import dataclass
import functools
import inspect
from pathlib import Path

from . import core
from .compiler import compile_model
from .core import Parameter, Shape


def _symbolic(value, name):
    """Promote numeric model inputs to named CAD parameters."""
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return Parameter(name, value)
    return value


def _model_function(function):
    """Call a function-based model with named symbolic CAD dimensions."""
    signature = inspect.signature(function)

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            bound.arguments[name] = _symbolic(value, name)
        return function(*bound.args, **bound.kwargs)

    return wrapped


def _design_object(cls, *args, **kwargs):
    """Construct normally first so dataclass validation sees plain values.

    Build-time numerical properties become Parameter objects; no user-written
    conversion boilerplate is needed. Frozen dataclasses are supported by
    setting values on the freshly constructed instance through object.__setattr__.
    """
    instance = cls(*args, **kwargs)
    build = getattr(instance, "build", None)
    if not callable(build):
        raise TypeError(f"{cls.__name__} must define build()")
    signature = inspect.signature(cls)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    for name, value in bound.arguments.items():
        if name not in vars(instance):
            continue
        symbolic = _symbolic(value, name)
        if symbolic is not value:
            object.__setattr__(instance, name, symbolic)
    result = build()
    if not isinstance(result, Shape):
        raise TypeError(
            f"{cls.__name__}.build() must finish with a Shape expression"
        )
    return result


def _implicit_shape(body):
    """Turn a trailing expression into an implicit return.

    This is a deliberate SCPF model convention; do not rewrite nested
    helper methods or unrelated Python functions. Explicit return stays
    valid. A last assignment alone is not treated as a CAD result.
    """
    if body and isinstance(body[-1], ast.Expr):
        body[-1] = ast.copy_location(ast.Return(value=body[-1].value), body[-1])


def run_script(path: str | Path) -> dict:
    """Run a trusted SCPF script and return its native command document."""
    path = Path(path)
    syntax = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if not syntax.body or not isinstance(syntax.body[-1], ast.Expr):
        raise SyntaxError("SCPF script must end with a model expression")
    last = syntax.body.pop()
    if not isinstance(last.value, ast.Call) or not isinstance(last.value.func, ast.Name):
        raise SyntaxError("SCPF script must end with a call such as Bracket()")
    name = last.value.func.id
    definitions = {
        item.name: item for item in syntax.body
        if isinstance(item, (ast.FunctionDef, ast.ClassDef))
    }
    definition = definitions.get(name)
    if definition is None:
        raise SyntaxError(f"the last call must use a defined model: {name}")

    context = {
        "__name__": "__scpf_model__",
        "__file__": str(path.resolve()),
        "dataclass": dataclass,
        "Box": core.Box,
        "Cube": core.Cube,
        "Cylinder": core.Cylinder,
        "Sphere": core.Sphere,
        "Polygon2D": core.Polygon2D,
        "Rectangle2D": core.Rectangle2D,
        "Circle2D": core.Circle2D,
        "Direction": core.Direction,
        "Edges": core.Edges,
        "Shape": core.Shape,
        "X": core.X,
        "Y": core.Y,
        "Z": core.Z,
    }
    if isinstance(definition, ast.FunctionDef):
        _implicit_shape(definition.body)
    else:
        for item in definition.body:
            if isinstance(item, ast.FunctionDef) and item.name == "build":
                _implicit_shape(item.body)
                break

    ast.fix_missing_locations(syntax)
    exec(compile(syntax, str(path), "exec"), context)
    if isinstance(definition, ast.FunctionDef):
        context[name] = _model_function(context[name])
        result = eval(
            compile(ast.Expression(body=last.value), str(path), "eval"), context
        )
    else:
        # Evaluate the final class construction with ordinary Python semantics,
        # then let SCPF convert the resulting object's numeric fields before
        # calling build().
        constructor = ast.Call(
            func=ast.Name(id="_scpf_design_object", ctx=ast.Load()),
            args=[ast.Name(id=name, ctx=ast.Load()), *last.value.args],
            keywords=last.value.keywords,
        )
        context["_scpf_design_object"] = _design_object
        ast.fix_missing_locations(constructor)
        result = eval(
            compile(ast.Expression(body=constructor), str(path), "eval"),
            context,
        )
    if not isinstance(result, Shape):
        raise TypeError(f"{name}() must produce a Shape")
    return compile_model(result, name)
