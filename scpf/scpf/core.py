"""Symbolic dimensions and model nodes. No SolidCraft transport or geometry.

All unadorned numerical values are millimetres. Model function arguments
become named parameters by the runner, not by user-written decorators.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Any


def number_text(value: float) -> str:
    return format(value, "g")


class Direction(str, Enum):
    """Extrusion direction relative to the sketch plane normal."""
    POSITIVE = "positive"
    NEGATIVE = "negative"


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

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value + other,
                              f"{self.name} + {number_text(other)} mm", (self,))
        return NotImplemented

    __radd__ = __add__

    def __neg__(self):
        return Expression(-self.value, f"-({self.name})", (self,))


@dataclass(frozen=True)
class Expression:
    value: float
    expression: str
    parameters: tuple[Parameter, ...]

    def __truediv__(self, other: float):
        if not isinstance(other, (float, int)) or other == 0:
            return NotImplemented
        return Expression(self.value / other, f"({self.expression}) / {number_text(other)}", self.parameters)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value + other,
                              f"{self.expression} + {number_text(other)} mm",
                              self.parameters)
        return NotImplemented

    __radd__ = __add__

    def __neg__(self):
        return Expression(-self.value, f"-({self.expression})", self.parameters)


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

    def extrude(self, distance, *, direction=Direction.POSITIVE):
        if self.kind not in ("polygon", "rectangle", "circle", "positioned", "union"):
            raise ValueError("extrude() requires a 2D profile")
        try:
            direction = Direction(direction)
        except ValueError as exc:
            raise ValueError("extrude direction must be Direction.POSITIVE or Direction.NEGATIVE") from exc
        return Shape("extrusion", (self, distance, direction.value))

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

    def at(self, x=0, y=0, z=0):
        """Place a 2D profile in world coordinates.

        For XY sketches, x and y locate the profile on its sketch plane;
        z offsets the sketch plane. The profile remains a reusable Shape.
        """
        if self.kind not in ("circle", "rectangle", "polygon", "positioned", "cylinder3d"):
            raise ValueError("at() currently supports planar profiles")
        return Shape("placed3d" if self.kind == "cylinder3d" else "positioned", (self, x, y, z))

    def pattern(self, *, x, y):
        if self.kind != "cylinder3d":
            raise ValueError("only cylinders support rectangular patterns in this PoP")
        return Shape("pattern", (self, x, y))

    def orient(self, *axes):
        if self.kind != "cylinder3d":
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


def Rectangle2D(width, depth):
    """An XY rectangle with its lower-left corner at the origin."""
    return Shape("rectangle", (width, depth))


def Circle2D(*, d=None, r=None):
    """An XY circle with diameter d or radius r."""
    if (d is None) == (r is None):
        raise ValueError("Circle2D requires exactly one of d= or r=")
    return Shape("circle", (d if d is not None else r * 2,))


def Polygon2D(points, *, plane="XY"):
    """A closed 2D polygon on XY, XZ or YZ."""
    coordinates = tuple(tuple(p) for p in points)
    if len(coordinates) < 3 or any(len(p) != 2 for p in coordinates):
        raise ValueError("Polygon2D requires at least three 2D points")
    if plane not in ("XY", "XZ", "YZ"):
        raise ValueError("unsupported sketch plane")
    return Shape("polygon", (coordinates, plane))


def Box(length, width, thickness):
    return Shape("box", (length, width, thickness))


def Cube(size):
    return Shape("cube", (size,))


def Sphere(radius):
    return Shape("sphere", (radius,))


def Cylinder(*, d, h):
    """A cylinder based at z=0; use .at(x, y, z) for placement."""
    return Shape("cylinder3d", (h, d))


X, Y, Z = "X", "Y", "Z"
