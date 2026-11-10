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


class Anchor(str, Enum):
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"


class Depth(str, Enum):
    THROUGH_ALL = "through_all"


class Axis(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


class Edges(Enum):
    """Named edge selections used by feature operations.

    Explicit edges can alternatively be supplied as 3D coordinates.
    """
    VERTICAL = "vertical"


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

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value - other,
                              f"{self.name} - {number_text(other)} mm", (self,))
        return NotImplemented

    def __neg__(self):
        return Expression(-self.value, f"-({self.name})", (self,))


@dataclass(frozen=True)
class Expression:
    value: float
    expression: str
    parameters: tuple[Parameter, ...]

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            return NotImplemented
        return Expression(self.value * other,
                          f"({self.expression}) * {number_text(other)}", self.parameters)

    __rmul__ = __mul__

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

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value - other,
                              f"({self.expression}) - {number_text(other)} mm", self.parameters)
        return NotImplemented

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

    def _apply_feature(self, feature, operation, *, on=None,
                       child=Anchor.BOTTOM, offset=(0, 0), name=None):
        """Apply a positioned CAD feature to this body in one operation.

        Placement and application are one step: the parent object is only
        mentioned once. Existing .on()/.attach() and +/- stay valid.
        """
        feature = _shape(feature)
        if on is not None:
            feature = feature.attach(
                self, parent=on, child=child, offset=offset)
        elif offset != (0, 0) or child is not Anchor.BOTTOM:
            raise ValueError("child/offset require on=Anchor.TOP/BOTTOM/CENTER")
        if name is not None:
            if not isinstance(name, str) or not name.isidentifier():
                raise ValueError("feature name must be a Python identifier")
            feature = Shape("labeled", (feature, name))
        return Shape(operation, (self, feature))

    def add(self, feature, *, on=None, child=Anchor.BOTTOM,
            offset=(0, 0), name=None):
        """Add a CAD feature, including native Hole features that cut material."""
        return self._apply_feature(feature, "union", on=on, child=child,
                                   offset=offset, name=name)

    def cut(self, feature, *, on=None, child=Anchor.BOTTOM,
            offset=(0, 0), name=None):
        """Remove material using a cutter or an explicitly sketched extrusion."""
        return self._apply_feature(feature, "difference", on=on, child=child,
                                   offset=offset, name=name)

    def move(self, x=0, y=0, z=0):
        """Translate a CSG shape by millimetres.

        Translates all primitives in a composite CSG model together.
        General feature-based box placement is not implemented yet.
        """
        offsets = (value_of(x), value_of(y), value_of(z))
        if not all(isfinite(v) for v in offsets):
            raise ValueError("move() requires finite coordinates")
        if self.kind in ("fillet", "pattern"):
            raise ValueError("move() currently supports only primitive and CSG shapes")
        return Shape("translated", (self, offsets))

    def extrude(self, distance, *, direction=Direction.POSITIVE):
        if self.kind not in ("polygon", "rectangle", "circle", "positioned", "union"):
            raise ValueError("extrude() requires a 2D profile")
        try:
            direction = Direction(direction)
        except ValueError as exc:
            raise ValueError("extrude direction must be Direction.POSITIVE or Direction.NEGATIVE") from exc
        return Shape("extrusion", (self, distance, direction.value))

    def fillet(self, radius, *, edges=Edges.VERTICAL):
        if edges is not Edges.VERTICAL:
            if not isinstance(edges, (list, tuple)) or not edges:
                raise ValueError("fillet edges must be Edges.VERTICAL or 3D edge points")
            for point in edges:
                if len(point) != 3:
                    raise ValueError("each fillet edge point must have x, y and z")
        return Shape("fillet", (self, radius, edges))

    def at(self, x=0, y=0, z=0):
        """Place a 2D profile in world coordinates.

        For XY sketches, x and y locate the profile on its sketch plane;
        z offsets the sketch plane. The profile remains a reusable Shape.
        """
        if self.kind not in ("circle", "rectangle", "polygon", "positioned", "cylinder", "hole"):
            raise ValueError("at() currently supports planar profiles")
        return Shape("placed3d" if self.kind in ("cylinder", "hole") else "positioned", (self, x, y, z))

    def pattern(self, *, count, spacing, axis):
        """Repeat a Hole or Cylinder at symmetric offsets along an XY axis."""
        if self.kind not in ("cylinder", "hole"):
            raise ValueError("pattern() supports Cylinder or Hole")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError("pattern count must be a positive integer")
        if value_of(spacing) <= 0:
            raise ValueError("pattern spacing must be positive")
        try:
            axis = Axis(axis)
        except ValueError as exc:
            raise ValueError("pattern axis must be Axis.X or Axis.Y") from exc
        if axis not in (Axis.X, Axis.Y):
            raise ValueError("only XY linear patterns are supported")
        return Shape("linear_pattern", (self, count, spacing, axis))

    def on(self, target, anchor=Anchor.CENTER, *, offset=(0, 0)):
        """Position a Cylinder or a linear pattern relative to an object.

        .on() aligns the cylinder's CENTER to the selected reference anchor.
        Both axes of offset are local to the XY face of the base plate.
        """
        child_anchor = Anchor.BOTTOM if (
            self.kind == "hole" or (
                self.kind == "linear_pattern" and self.data[0].kind == "hole"
            )
        ) else Anchor.CENTER
        return self._anchor_to(target, anchor, child_anchor, offset)

    def attach(self, target, *, parent=Anchor.TOP, child=Anchor.BOTTOM,
               offset=(0, 0)):
        """Match a parent anchor to a child anchor (BOSL2-inspired)."""
        return self._anchor_to(target, parent, child, offset)

    def _anchor_to(self, target, parent_anchor, child_anchor, offset):
        if self.kind not in ("cylinder", "linear_pattern", "hole"):
            raise ValueError("on()/attach() currently support Cylinder, Hole and their linear patterns")
        if not isinstance(target, Shape):
            raise TypeError("anchor target must be an existing Shape")
        try:
            parent_anchor = Anchor(parent_anchor)
            child_anchor = Anchor(child_anchor)
        except ValueError as exc:
            raise ValueError("unknown parent or child anchor") from exc
        if not isinstance(offset, (tuple, list)) or len(offset) != 2:
            raise ValueError("offset must be a pair (x, y)")
        for value in offset:
            value_of(value)
        return Shape("anchored", (self, target, parent_anchor, child_anchor, tuple(offset)))

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


def Sphere(radius):
    return Shape("sphere", (radius,))


def Cylinder(*, d, h):
    """A cylinder based at z=0; use .at(x, y, z) for placement."""
    return Shape("cylinder", (h, d))


def Hole(*, d, depth=Depth.THROUGH_ALL):
    """A native SolidCraft hole feature; unlike Cylinder it is not a solid.

    Place it on an existing solid face using .on(parent, Anchor.TOP).
    A symbolic or numeric depth drills a blind hole; the default is through all.
    """
    if value_of(d) <= 0:
        raise ValueError("hole diameter must be positive")
    if depth is not Depth.THROUGH_ALL and value_of(depth) <= 0:
        raise ValueError("hole depth must be positive or Depth.THROUGH_ALL")
    return Shape("hole", (d, depth))


X, Y, Z = "X", "Y", "Z"
