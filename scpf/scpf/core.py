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
    INNER_BOTTOM = "inner_bottom"


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


class Faces(Enum):
    """Named planar face selections for feature operations."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"


@dataclass(frozen=True)
class _BoundOffset:
    """Position relative to one named axis of the parent bounds."""
    axis: str
    reference: str
    delta: Any = 0

    def __add__(self, value):
        if isinstance(value, bool):
            return NotImplemented
        delta = value if self.delta == 0 else self.delta + value
        return _BoundOffset(self.axis, self.reference, delta)

    __radd__ = __add__

    def __sub__(self, value):
        if isinstance(value, bool):
            return NotImplemented
        delta = -value if self.delta == 0 else self.delta - value
        return _BoundOffset(self.axis, self.reference, delta)


class _AxisRef(str):
    """Axis token that also exposes parent-bound placement selectors."""

    @property
    def MIN(self):
        return _BoundOffset(str(self), "min")

    @property
    def CENTER(self):
        return _BoundOffset(str(self), "center")

    @property
    def MAX(self):
        return _BoundOffset(str(self), "max")


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
        elif isinstance(value, _BoundOffset):
            for param in parameters_in(value.delta):
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
        if self.kind in ("fillet", "shell", "pattern"):
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

    def shell(self, thickness, *, open=Faces.TOP):
        """Hollow a solid to an even wall thickness and leave selected faces open."""
        value_of(thickness)
        if isinstance(open, Faces):
            faces = (open,)
        elif isinstance(open, (list, tuple)) and open:
            try:
                faces = tuple(Faces(face) for face in open)
            except ValueError as exc:
                raise ValueError("shell open faces must use Faces values") from exc
        else:
            raise ValueError("shell open must be a Faces value or non-empty sequence")
        return Shape("shell", (self, thickness, faces))

    def at(self, x=0, y=0, z=0):
        """Place a supported profile, primitive or feature at world coordinates.

        For XY sketches, x and y locate the profile on its sketch plane and z
        offsets that plane. For 3D and plastic features the point is the native
        SolidCraft authoring position.
        """
        if self.kind not in (
            "circle", "rectangle", "polygon", "positioned", "cylinder", "hole",
            "lip", "snap_fit", "boss", "rest",
        ):
            raise ValueError("at() does not support this shape")
        return Shape(
            "placed3d" if self.kind in (
                "cylinder", "hole", "lip", "snap_fit", "boss", "rest"
            ) else "positioned",
            (self, x, y, z),
        )

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

    def attach(self, target, *, parent=Anchor.TOP, child=Anchor.BOTTOM,
               offset=(0, 0)):
        """Match a parent anchor to a child anchor (BOSL2-inspired)."""
        return self._anchor_to(target, parent, child, offset)

    def _anchor_to(self, target, parent_anchor, child_anchor, offset):
        if self.kind not in (
            "cylinder", "linear_pattern", "hole",
            "lip", "snap_fit", "boss", "rest",
        ):
            raise ValueError(
                "attach() supports Cylinder, Hole, plastic features and their supported patterns"
            )
        if not isinstance(target, Shape):
            raise TypeError("anchor target must be an existing Shape")
        try:
            parent_anchor = Anchor(parent_anchor)
            child_anchor = Anchor(child_anchor)
        except ValueError as exc:
            raise ValueError("unknown parent or child anchor") from exc
        if not isinstance(offset, (tuple, list)) or len(offset) != 2:
            raise ValueError("offset must be a pair (x, y)")
        for index, value in enumerate(offset):
            if isinstance(value, _BoundOffset):
                expected_axis = "X" if index == 0 else "Y"
                if value.axis != expected_axis:
                    raise ValueError(
                        f"offset position {index} requires {expected_axis} bounds"
                    )
                if not isfinite(value_of(value.delta)):
                    raise ValueError("bound offset must be finite")
            else:
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
    """A hole intent; unlike Cylinder it is not positive solid geometry.

    Attach it to the face where drilling starts. The compiler chooses the
    native SolidCraft sketch/cut representation. A numeric depth makes a
    blind hole; the default drills through the supported body.
    """
    if value_of(d) <= 0:
        raise ValueError("hole diameter must be positive")
    if depth is not Depth.THROUGH_ALL and value_of(depth) <= 0:
        raise ValueError("hole depth must be positive or Depth.THROUGH_ALL")
    return Shape("hole", (d, depth))


def Lip(*, width, height):
    """Plastic enclosure lip placed by a point on a shelled rim face."""
    return Shape("lip", (width, height))


def SnapFit(*, length, thickness, width, catch_depth, catch_length,
            hook, direction=None):
    """Cantilever plastic snap fit placed by a point on its supporting face."""
    hook = tuple(hook)
    if len(hook) != 3:
        raise ValueError("SnapFit hook must be a 3D direction")
    if direction is not None:
        direction = tuple(direction)
        if len(direction) != 3:
            raise ValueError("SnapFit direction must be a 3D direction")
    return Shape(
        "snap_fit",
        (length, thickness, width, catch_depth, catch_length, hook, direction),
    )


def Boss(*, d, h, hole_d=None, direction=None):
    """Plastic screw boss placed by a point on its supporting face."""
    if direction is not None:
        direction = tuple(direction)
        if len(direction) != 3:
            raise ValueError("Boss direction must be a 3D direction")
    return Shape("boss", (d, h, hole_d, direction))


def Rest(*, width, height, length=None, along=None, direction=None):
    """Plastic support pad placed by its centre point on a supporting face."""
    if along is not None:
        along = tuple(along)
        if len(along) != 3:
            raise ValueError("Rest along must be a 3D direction")
    if direction is not None:
        direction = tuple(direction)
        if len(direction) != 3:
            raise ValueError("Rest direction must be a 3D direction")
    return Shape("rest", (width, height, length, along, direction))


X, Y, Z = _AxisRef("X"), _AxisRef("Y"), _AxisRef("Z")
