"""Execute a short Python CAD script and compile its final expression.

Unlike a regular Python module, an SCPF model.rs-equivalent ends with the
Shape expression to build, e.g. `Plate()`. No show(), imports, main(), or
manual parameter wrappers are required.

SCPF scripts are Python code and must be treated as trusted input.
"""
import ast
import functools
import inspect
from pathlib import Path

from . import core
from .compiler import compile_model
from .core import Parameter, Shape


def _model_function(function):
    """Call a Python model with named symbolic CAD dimensions."""
    signature = inspect.signature(function)

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            # Parameter metadata comes from the Python function signature.
            # Explicitly provided numerical arguments remain editable.
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                bound.arguments[name] = Parameter(name, value)
        return function(*bound.args, **bound.kwargs)

    return wrapped


def run_script(path: str | Path) -> dict:
    """Run a trusted SCPF script and return its generated command JSON."""
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    syntax = ast.parse(source, filename=str(path))
    if not syntax.body or not isinstance(syntax.body[-1], ast.Expr):
        raise SyntaxError("SCPF script must end with a Shape expression")
    last = syntax.body.pop()
    if not isinstance(last.value, ast.Call) or not isinstance(last.value.func, ast.Name):
        raise SyntaxError("SCPF script must end with a call such as Plate()")
    name = last.value.func.id
    declarations = {
        item.name for item in syntax.body if isinstance(item, ast.FunctionDef)
    }
    if name not in declarations:
        raise SyntaxError(f"the final expression must call a model function: {name}")

    context = {
        "__name__": "__scpf_model__",
        "__file__": str(path.resolve()),
        "Box": core.Box,
        "Cube": core.Cube,
        "Cylinder": core.Cylinder,
        "Sphere": core.Sphere,
        "Shape": core.Shape,
        "X": core.X,
        "Y": core.Y,
        "Z": core.Z,
    }
    ast.fix_missing_locations(syntax)
    exec(compile(syntax, str(path), "exec"), context)
    context[name] = _model_function(context[name])
    result = eval(
        compile(ast.Expression(body=last.value), str(path), "eval"),
        context,
    )
    if not isinstance(result, Shape):
        raise TypeError(f"{name}() must produce a Shape")
    return compile_model(result, name)
