"""Execute a trusted SCPF script, then compile its final model expression.

Scripts end with a function call (Plate()) or a dataclass design instance
(Bracket()). SCPF automatically calls build() on a design instance.
Within the model's build() or final function, a last geometry expression
acts as an implicit return. No show() or main() is required.
"""
import ast
from contextlib import contextmanager
from dataclasses import dataclass, is_dataclass
import functools
import inspect
from pathlib import Path
import sys

from . import core
from .compiler import compile_model
from .core import Expression, Parameter, Shape, pv
from .assembly import compile_assembly
from .model_objects import Assembly, ModelDefinition, ModelInstance
from .history import History, behavior
from .explicit_sketch import Sketch


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


def _plain_model_fields(cls):
    """Ordered numeric class attributes, including inherited model fields."""
    fields = {}
    # Base model dimensions come first; subclasses may override defaults
    # without reimplementing build(). Existing key order stays stable.
    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for name, value in vars(base).items():
            if (not name.startswith("_")
                    and isinstance(value, (int, float))
                    and not isinstance(value, bool)):
                fields[name] = value
    return list(fields.items())


def _parameter_input(value, name):
    """Bind a model input to a fresh named parameter.

    Parent Parameter/Expression values are accepted directly. Their current
    numeric value seeds the child parameter; the child keeps its own name.
    """
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a numeric model parameter")
    if isinstance(value, (Parameter, Expression)):
        concrete = pv(value)
    elif isinstance(value, (int, float)):
        concrete = float(value)
    else:
        raise TypeError(f"{name} must be a numeric model parameter")
    return concrete, Parameter(name, concrete)


def _plain_model_data(cls, *args, **kwargs):
    """Instantiate a plain model and return its concrete parameter values."""
    fields = _plain_model_fields(cls)
    names = [name for name, _ in fields]
    if len(args) > len(fields):
        raise TypeError(
            f"{cls.__name__}() takes at most {len(fields)} model arguments"
        )

    values = dict(fields)
    assigned = set()
    for (name, _), value in zip(fields, args):
        values[name] = value
        assigned.add(name)

    for name, value in kwargs.items():
        if name not in values:
            raise TypeError(
                f"{cls.__name__}() got an unexpected model parameter {name!r}"
            )
        if name in assigned:
            raise TypeError(
                f"{cls.__name__}() got multiple values for parameter {name!r}"
            )
        values[name] = value
        assigned.add(name)

    instance = cls()
    concrete = []
    for name in names:
        value, symbolic = _parameter_input(values[name], name)
        concrete.append((name, value))
        object.__setattr__(instance, name, symbolic)
    return instance, tuple(concrete)


def _plain_model_instance(cls, *args, **kwargs):
    """Instantiate a plain SCPF model class without requiring @dataclass."""
    return _plain_model_data(cls, *args, **kwargs)[0]


def _parameterized_instance(cls, *args, **kwargs):
    """Construct one model object and retain concrete values for reuse."""
    if not is_dataclass(cls):
        return _plain_model_data(cls, *args, **kwargs)

    instance = cls(*args, **kwargs)
    signature = inspect.signature(cls)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    concrete = []
    for name, value in bound.arguments.items():
        if name not in vars(instance):
            continue
        if isinstance(value, (int, float, Parameter, Expression)) and not isinstance(value, bool):
            number, symbolic = _parameter_input(value, name)
            concrete.append((name, number))
            object.__setattr__(instance, name, symbolic)
    return instance, tuple(concrete)


def _build_object(cls, *args, **kwargs):
    """Build one user model and return its result plus concrete parameters."""
    instance, concrete = _parameterized_instance(cls, *args, **kwargs)
    build = getattr(instance, "build", None)
    if not callable(build):
        raise TypeError(f"{cls.__name__} must define build()")
    return build(), concrete


def _design_object(cls, *args, **kwargs):
    """Build the root model object.

    A root model may still produce one Shape, or it may compose reusable model
    instances into an Assembly.
    """
    result, _ = _build_object(cls, *args, **kwargs)
    if not isinstance(result, (Shape, ModelInstance, Assembly)):
        raise TypeError(
            f"{cls.__name__}.build() must finish with a Shape or assembly"
        )
    return result


def _reusable_model_object(cls, *args, **kwargs):
    """Build a nested user model as a reusable component definition."""
    result, concrete = _build_object(cls, *args, **kwargs)
    if not isinstance(result, Shape):
        raise TypeError(
            f"{cls.__name__}.build() must produce one Shape when reused as a component"
        )
    return ModelInstance(
        ModelDefinition(
            class_name=cls.__name__,
            parameters=concrete,
            shape=result,
        )
    )


def _model_factory(cls):
    """Replace a nested class name with a transparent reusable-model factory."""
    @functools.wraps(cls)
    def factory(*args, **kwargs):
        return _reusable_model_object(cls, *args, **kwargs)
    return factory


def component(cls):
    """Declare an imported CAD model class as a reusable SCPF component."""
    if not isinstance(cls, type) or not callable(getattr(cls, "build", None)):
        raise TypeError("component() expects a model class with build()")
    return _model_factory(cls)


def _reusable_assembly_object(cls, *args, **kwargs):
    """Build an imported assembly class without exposing build_* helpers."""
    result, _ = _build_object(cls, *args, **kwargs)
    if not isinstance(result, (ModelInstance, Assembly)):
        raise TypeError(
            f"{cls.__name__}.build() must produce a component or assembly"
        )
    return result


def _assembly_factory(cls):
    @functools.wraps(cls)
    def factory(*args, **kwargs):
        return _reusable_assembly_object(cls, *args, **kwargs)
    return factory


def assembly(cls):
    """Declare an imported class whose build() returns an SCPF assembly."""
    if not isinstance(cls, type) or not callable(getattr(cls, "build", None)):
        raise TypeError("assembly() expects a model class with build()")
    return _assembly_factory(cls)


def _implicit_shape(body):
    """Turn a trailing expression into an implicit return.

    This is a deliberate SCPF model convention; do not rewrite nested
    helper methods or unrelated Python functions. Explicit return stays
    valid. A last assignment alone is not treated as a CAD result.
    """
    if body and isinstance(body[-1], ast.Expr):
        body[-1] = ast.copy_location(ast.Return(value=body[-1].value), body[-1])


@contextmanager
def _model_import_context(path: Path):
    """Make project-local component imports available for a model script.

    A script in `<project>/models/<slug>/scpf/model.py` may import
    `models.components.*`. This must work whether the user runs SCPF from
    the repository root or from the script's own directory.

    Only the execution of this trusted script receives these import paths.
    Restore sys.path afterwards; do not require user-set PYTHONPATH.
    """
    roots = [path.parent]
    for ancestor in path.parents:
        if ancestor.name == "models":
            roots.append(ancestor.parent)
            break

    original = sys.path[:]
    original_dont_write_bytecode = sys.dont_write_bytecode
    try:
        # Model projects often split parts and assemblies over small Python
        # modules. Keep those source trees clean: imported model modules are
        # transient build input and do not need adjacent __pycache__ files.
        sys.dont_write_bytecode = True
        for root in reversed(roots):
            folder = str(root)
            if folder in sys.path:
                sys.path.remove(folder)
            sys.path.insert(0, folder)
        yield
    finally:
        sys.path[:] = original
        sys.dont_write_bytecode = original_dont_write_bytecode


def run_script(path: str | Path) -> dict:
    """Run a trusted SCPF script and return its native command document."""
    path = Path(path).resolve()
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
        "Cylinder": core.Cylinder,
        "Hole": core.Hole,
        "Lip": core.Lip,
        "SnapFit": core.SnapFit,
        "Boss": core.Boss,
        "Rest": core.Rest,
        "Depth": core.Depth,
        "Sphere": core.Sphere,
        "Polygon2D": core.Polygon2D,
        "Rectangle2D": core.Rectangle2D,
        "RoundedRectangle2D": core.RoundedRectangle2D,
        "Circle2D": core.Circle2D,
        "Text2D": core.Text2D,
        "Direction": core.Direction,
        "Edges": core.Edges,
        "Faces": core.Faces,
        "Anchor": core.Anchor,
        "Axis": core.Axis,
        "Shape": core.Shape,
        "X": core.X,
        "Y": core.Y,
        "Z": core.Z,
        "History": History,
        "behavior": behavior,
        "Sketch": Sketch,
    }
    if isinstance(definition, ast.FunctionDef):
        _implicit_shape(definition.body)

    model_classes = {}
    for item in syntax.body:
        if not isinstance(item, ast.ClassDef):
            continue
        build_method = next(
            (member for member in item.body
             if isinstance(member, ast.FunctionDef) and member.name == "build"),
            None,
        )
        if build_method is not None:
            _implicit_shape(build_method.body)
            model_classes[item.name] = item

    ast.fix_missing_locations(syntax)
    with _model_import_context(path):
        exec(compile(syntax, str(path), "exec"), context)

        root_class = context.get(name) if isinstance(definition, ast.ClassDef) else None
        for class_name in model_classes:
            if class_name != name:
                context[class_name] = _model_factory(context[class_name])

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
                args=[ast.Name(id="_scpf_root_class", ctx=ast.Load()), *last.value.args],
                keywords=last.value.keywords,
            )
            context["_scpf_design_object"] = _design_object
            context["_scpf_root_class"] = root_class
            ast.fix_missing_locations(constructor)
            result = eval(
                compile(ast.Expression(body=constructor), str(path), "eval"),
                context,
            )
    if isinstance(result, Shape):
        return compile_model(result, name)
    if isinstance(result, (ModelInstance, Assembly)):
        return compile_assembly(result, name)
    raise TypeError(f"{name}() must produce CAD geometry or an assembly")
