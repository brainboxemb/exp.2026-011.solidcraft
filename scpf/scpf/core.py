"""Symbolic dimensions and model nodes. No SolidCraft transport or geometry.

All unadorned numerical values are millimetres. Model function arguments
become named parameters by the runner, not by user-written decorators.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Any


def number_text(value: float) -> str:
    return format(value, "g")


@dataclass(frozen=True)
class Parameter:
    name: str
    value: float

    def __post_init__(self):
        if not self.name.isidentifier():
            raise ValueError(f"invalid CAD parameter name: {self.name}")
        if not isinstance(self.value, (int, float)) or not isfinite(self.value):
            raise ValueError(f"invalid CAD parameter value: {self.name}")

    @property
    def expression(self):
        return self.name

    def __truediv__(self, other: float):
        if not isinstance(other, (float, int)) or other == 0:
            return NotImplemented
        return Expression(self.value / other, f"{self.name} / {number_text(other)}", (self,))

    def __mul__(self, other: float):
        if not isinstance(other, (float, int)):
            return NotImplemented
        return Expression(self.value * other, f"{self.name} * {number_text(other)}", (self,))

    __rmul__ = __mul__


@dataclass(frozen=True)
class Expression:
    value: float
    expression: str
    parameters: tuple[Parameter, ...]

    def __truediv__(self, other: float):
        if not isinstance(other, (float, int)) or other == 0:
            return NotImplemented
        return Expression(self.value / other, f"({self.expression}) / {number_text(other)}", self.parameters)


def value_of(dim) -> float:
    if isinstance(dim, Parameter):
        return dim.value
    if isinstance(dim, Expression):
        return dim.value
    if isinstance(dim, (int, float)):
        return float(dim)
    raise TypeError(f"expected a CAD dimension, got {type(dim).__name__}")


def command_value(dim):
    return dim.expression if isinstance(dim, (Parameter, Expression)) else dim


def parameters_in(*values) -> tuple[Parameter, ...]:
    found = {}
    for value in values:
        if isinstance(value, Parameter):
            found.setdefault(value.name, value)
        elif isinstance(value, Expression):
            for param in value.parameters:
                found.setdefault(param.name, param)
    return tuple(found.values())


@dataclass(frozen=True)
class Shape:
    kind: str
    data: Any

    def __and__(self, other):
        return Shape("intersection", (self, _shape(other)))

    def __add__(self, other):
        return Shape("union", (self, _shape(other)))

    def __or__(self, other):
        return self + other

    def __sub__(self, other):
        return Shape("difference", (self, _shape(other)))

    def move(self, x=0, y=0, z=0):
        """Translate a CSG shape by millimetres.

        Translates all primitives in a composite CSG model together.
        General feature-based box placement is not implemented yet.
        """
        offsets = (value_of(x), value_of(y), value_of(z))
        if not all(isfinite(v) for v in offsets):
            raise ValueError("move() requires finite coordinates")
        if self.kind in ("box", "fillet", "pattern"):
            raise ValueError("move() currently supports only CSG shapes")
        return Shape("translated", (self, offsets))

    def extrude(self, distance, *, direction="positive"):
        if self.kind != "polygon":
            raise ValueError("extrude() currently requires a Polygon")
        if direction not in ("positive", "negative"):
            raise ValueError("extrude direction must be positive or negative")
        return Shape("extrusion", (self, distance, direction))

    def fillet(self, radius, *, edges="vertical"):
        if edges != "vertical":
            if not isinstance(edges, (list, tuple)) or not edges:
                raise ValueError("fillet edges must be 'vertical' or 3D edge points")
            for point in edges:
                if len(point) != 3:
                    raise ValueError("each fillet edge point must have x, y and z")
        return Shape("fillet", (self, radius, edges))

    def holes(self, centers, *, diameter, depth, plane="XY"):
        """Cut XY sketch circles; infer cut direction from the solid profile."""
        if plane != "XY":
            raise ValueError("the current holes() compiler supports only XY")
        positions = tuple(tuple(p) for p in centers)
        if not positions or any(len(p) != 2 for p in positions):
            raise ValueError("holes require at least one (x, y) centre")
        return Shape("holes", (self, positions, diameter, depth, plane))

    def pattern(self, *, x, y):
        if self.kind != "cylinder":
            raise ValueError("only cylinders support rectangular patterns in this PoP")
        return Shape("pattern", (self, x, y))

    def orient(self, *axes):
        if self.kind != "cylinder":
            raise ValueError("only cylinders support orient()")
        if len(axes) == 1 and isinstance(axes[0], (tuple, list)):
            axes = tuple(axes[0])
        if not axes or any(a not in ("X", "Y", "Z") for a in axes):
            raise ValueError("orient() requires X, Y, and/or Z")
        return Shape("orient", (self, tuple(axes)))


def _shape(value):
    if not isinstance(value, Shape):
        raise TypeError("boolean operations require a Shape")
    return value


def Polygon(points, *, plane="XY"):
    """Create a closed planar profile, extrudable by SolidCraft."""
    coordinates = tuple(tuple(p) for p in points)
    if len(coordinates) < 3 or any(len(p) != 2 for p in coordinates):
        raise ValueError("Polygon needs at least three (u, v) points")
    if plane not in ("XY", "XZ", "YZ"):
        raise ValueError("unsupported sketch plane")
    return Shape("polygon", (coordinates, plane))


def Box(length, width, thickness):
    return Shape("box", (length, width, thickness))


def Cube(size):
    return Shape("cube", (size,))


def Sphere(radius):
    return Shape("sphere", (radius,))


def Cylinder(height, diameter):
    return Shape("cylinder", (height, diameter))


X, Y, Z = "X", "Y", "Z"
