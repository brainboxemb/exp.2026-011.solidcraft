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
    SYMMETRIC = "symmetric"


class Anchor(str, Enum):
    """Assembly attachment references between reusable components."""
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"
    FRONT_TOP_LEFT = "front_top_left"
    FRONT_TOP_RIGHT = "front_top_right"
    FRONT_BOTTOM_LEFT = "front_bottom_left"
    FRONT_BOTTOM_RIGHT = "front_bottom_right"
    BACK_TOP_LEFT = "back_top_left"
    BACK_TOP_RIGHT = "back_top_right"
    BACK_BOTTOM_LEFT = "back_bottom_left"
    BACK_BOTTOM_RIGHT = "back_bottom_right"
    INNER_BOTTOM = "inner_bottom"


@dataclass(frozen=True)
class AnchorFrame:
    """One local attachment frame for a reusable component occurrence.

    A frame may be returned from a component's anchors() mapping or supplied
    directly to attach() by an assembly. origin is a point in component-local
    millimetres; z and x define the attachment orientation.
    """

    origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    z: tuple[float, float, float] = (0.0, 0.0, 1.0)
    x: tuple[float, float, float] = (1.0, 0.0, 0.0)

    def __post_init__(self):
        vectors = {}
        for name, value in (
            ("origin", self.origin),
            ("z", self.z),
            ("x", self.x),
        ):
            if not isinstance(value, (tuple, list)) or len(value) != 3:
                raise ValueError(f"AnchorFrame {name} must be an XYZ triple")
            if any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not isfinite(v)
                for v in value
            ):
                raise ValueError(
                    f"AnchorFrame {name} must contain finite numeric values"
                )
            vectors[name] = tuple(float(v) for v in value)

        z = vectors["z"]
        x = vectors["x"]
        if sum(v * v for v in z) <= 0 or sum(v * v for v in x) <= 0:
            raise ValueError("AnchorFrame x and z directions must be non-zero")
        cross = (
            z[1] * x[2] - z[2] * x[1],
            z[2] * x[0] - z[0] * x[2],
            z[0] * x[1] - z[1] * x[0],
        )
        if sum(v * v for v in cross) <= 1e-18:
            raise ValueError("AnchorFrame x direction must not be parallel to z")

        object.__setattr__(self, "origin", vectors["origin"])
        object.__setattr__(self, "z", z)
        object.__setattr__(self, "x", x)


@dataclass(frozen=True)
class AnchorTopology:
    """Topology-backed attachment reference on a planar-face edge.

    edge is a pick point on the edge and on selects the adjacent planar face.
    corner optionally selects one endpoint. SolidCraft keeps the selected
    topology by name, so the reference follows dimension changes. z and x may
    override the resulting frame orientation.
    """

    edge: tuple[float, float, float]
    on: tuple[float, float, float]
    corner: tuple[float, float, float] | None = None
    z: tuple[float, float, float] | None = None
    x: tuple[float, float, float] | None = None

    def __post_init__(self):
        for name in ("edge", "on", "corner", "z", "x"):
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(value, (tuple, list)) or len(value) != 3:
                raise ValueError(f"AnchorTopology {name} must be an XYZ triple")
            if any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not isfinite(v)
                for v in value
            ):
                raise ValueError(
                    f"AnchorTopology {name} must contain finite numeric values"
                )
            object.__setattr__(self, name, tuple(float(v) for v in value))

        if self.z is not None and sum(v * v for v in self.z) <= 0:
            raise ValueError("AnchorTopology z direction must be non-zero")
        if self.x is not None and sum(v * v for v in self.x) <= 0:
            raise ValueError("AnchorTopology x direction must be non-zero")
        if self.z is not None and self.x is not None:
            cross = (
                self.z[1] * self.x[2] - self.z[2] * self.x[1],
                self.z[2] * self.x[0] - self.z[0] * self.x[2],
                self.z[0] * self.x[1] - self.z[1] * self.x[0],
            )
            if sum(v * v for v in cross) <= 1e-18:
                raise ValueError(
                    "AnchorTopology x direction must not be parallel to z"
                )


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

    @staticmethod
    def from_profile(*segment_ids, sides="both"):
        """Select named 2D sketch segments on the broad faces of an extrusion.

        IDs are defined by Polygon2D(ids=...). At compilation time SCPF
        resolves them into points accepted by SolidCraft's fillet/chamfer API.
        Wildcards (e.g. "outer_*") match sketch IDs, not 3D edge names.
        """
        if not segment_ids or any(not isinstance(name, str) or not name
                                  for name in segment_ids):
            raise ValueError("provide one or more profile segment IDs or patterns")
        if sides != "both":
            raise ValueError("profile-edge selection currently supports sides='both'")
        return _ProfileEdgeSelection(tuple(segment_ids), sides)

    @staticmethod
    def from_vertices(*vertex_ids):
        """Select extrusion-axis edges grown from named profile vertices."""
        if not vertex_ids or any(not isinstance(name, str) or not name
                                 for name in vertex_ids):
            raise ValueError("provide named profile vertices")
        return _ProfileEdgeSelection(tuple(vertex_ids), "axis", "vertices")


@dataclass(frozen=True)
class _ProfileEdgeSelection:
    patterns: tuple[str, ...]
    sides: str
    kind: str = "segments"


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
        if isinstance(other, (Parameter, Expression)):
            return Expression(
                self.value + pv(other),
                f"{self.name} + ({command_value(other)})",
                parameters_in(self, other),
            )
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value - other,
                              f"{self.name} - {number_text(other)} mm", (self,))
        if isinstance(other, (Parameter, Expression)):
            return Expression(
                self.value - pv(other),
                f"{self.name} - ({command_value(other)})",
                parameters_in(self, other),
            )
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
        if isinstance(other, (Parameter, Expression)):
            return Expression(
                self.value + pv(other),
                f"({self.expression}) + ({command_value(other)})",
                parameters_in(self, other),
            )
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Expression(self.value - other,
                              f"({self.expression}) - {number_text(other)} mm", self.parameters)
        if isinstance(other, (Parameter, Expression)):
            return Expression(
                self.value - pv(other),
                f"({self.expression}) - ({command_value(other)})",
                parameters_in(self, other),
            )
        return NotImplemented

    def __neg__(self):
        return Expression(-self.value, f"-({self.expression})", self.parameters)


def pv(dim) -> float:
    """Return the concrete Python value of a symbolic CAD dimension.

    Use this only when Python itself needs a number for control flow or
    placement logic. Geometry should normally keep Parameter/Expression
    objects symbolic so SolidCraft receives editable named parameters.
    """
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
    history: Any = None

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
        offsets = (pv(x), pv(y), pv(z))
        if not all(isfinite(v) for v in offsets):
            raise ValueError("move() requires finite coordinates")
        if self.kind in ("fillet", "shell", "pattern"):
            raise ValueError("move() currently supports only primitive and CSG shapes")
        return Shape("translated", (self, offsets))

    def taper(self, *, from_z, inset):
        """Make a box with a flat front and continuously tapered rear walls.

        The rear perimeter retreats by inset per side, from from_z to the
        box's full height. This produces native editable sketches and loft.
        """
        if self.kind != "box":
            raise ValueError("taper() currently requires a Box")
        width, height, depth = self.data
        if not 0 < pv(from_z) < pv(depth):
            raise ValueError("taper from_z must lie within the box depth")
        if not 0 < pv(inset) * 2 < min(pv(width), pv(height)):
            raise ValueError("taper inset must be below half the footprint")
        return Shape("tapered_box", (self, from_z, inset))

    def extrude(self, distance, *, direction=Direction.POSITIVE):
        if self.kind not in ("polygon", "rectangle", "circle", "positioned", "union"):
            raise ValueError("extrude() requires a 2D profile")
        try:
            direction = Direction(direction)
        except ValueError as exc:
            raise ValueError(
                "extrude direction must be POSITIVE, NEGATIVE or SYMMETRIC"
            ) from exc
        return Shape("extrusion", (self, distance, direction.value))

    def fillet(self, radius, *, edges=Edges.VERTICAL):
        if edges is not Edges.VERTICAL and not isinstance(edges, _ProfileEdgeSelection):
            if not isinstance(edges, (list, tuple)) or not edges:
                raise ValueError("fillet edges must be Edges.VERTICAL or 3D edge points")
            for point in edges:
                if len(point) != 3:
                    raise ValueError("each fillet edge point must have x, y and z")
        return Shape("fillet", (self, radius, edges))

    def chamfer(self, distance, *, edges):
        """Chamfer explicitly selected solid edges by an equal distance."""
        pv(distance)
        if isinstance(edges, _ProfileEdgeSelection):
            return Shape("chamfer", (self, distance, edges))
        if not isinstance(edges, (list, tuple)) or not edges:
            raise ValueError("chamfer edges must be a non-empty sequence of 3D edge points")
        for point in edges:
            if not isinstance(point, (list, tuple)) or len(point) != 3:
                raise ValueError("each chamfer edge point must have x, y and z")
            for coordinate in point:
                pv(coordinate)
        return Shape("chamfer", (self, distance, tuple(tuple(p) for p in edges)))

    def shell(self, thickness, *, open=Faces.TOP):
        """Hollow a solid to an even wall thickness and leave selected faces open."""
        pv(thickness)
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

    def with_material(self, name, *, density_g_cm3, color=None):
        """Assign one design-owned physical material to the final body."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("material name must be a non-empty string")
        if not isinstance(density_g_cm3, (int, float)) or not 0 < density_g_cm3 <= 1000:
            raise ValueError("material density must be in (0, 1000] g/cm3")
        if color is not None and (not isinstance(color, str) or
                                  len(color) != 7 or color[0] != "#" or
                                  any(c not in "0123456789abcdefABCDEF" for c in color[1:])):
            raise ValueError("material color must be a #RRGGBB hex string")
        return Shape("material_assignment", (self, name, density_g_cm3, color))

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
        if pv(spacing) <= 0:
            raise ValueError("pattern spacing must be positive")
        try:
            axis = Axis(axis)
        except ValueError as exc:
            raise ValueError("pattern axis must be Axis.X or Axis.Y") from exc
        if axis not in (Axis.X, Axis.Y):
            raise ValueError("only XY linear patterns are supported")
        return Shape("linear_pattern", (self, count, spacing, axis))

    def on(self, target, *, face=Faces.TOP, offset=(0, 0)):
        """Place a supported feature on a selected face of another shape.

        This is simple within-component placement. Use Faces to choose the
        target surface; assembly Anchor values belong to ModelInstance.attach().
        """
        try:
            face = Faces(face)
        except ValueError as exc:
            raise ValueError("on() face must be a Faces value") from exc
        face_to_anchor = {
            Faces.TOP: Anchor.TOP,
            Faces.BOTTOM: Anchor.BOTTOM,
        }
        if face not in face_to_anchor:
            raise ValueError("on() currently supports Faces.TOP or Faces.BOTTOM")
        return self._anchor_to(target, face_to_anchor[face], Anchor.BOTTOM, offset)

    def attach(self, target, *, parent=Anchor.TOP, child=Anchor.BOTTOM,
               offset=(0, 0)):
        """Legacy explicit feature anchoring; prefer on() for simple placement."""
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
                if not isfinite(pv(value.delta)):
                    raise ValueError("bound offset must be finite")
            else:
                pv(value)
        return Shape(
            "anchored",
            (self, target, parent_anchor, child_anchor, tuple(offset)),
            self.history,
        )

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


def Text2D(text, *, height=6.0, font="DejaVu Sans Bold"):
    """Editable sketch lettering (height is capital height, in mm)."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text2D requires non-empty text")
    if not isinstance(font, str) or not font.strip():
        raise ValueError("Text2D requires a font family")
    if pv(height) <= 0:
        raise ValueError("Text2D height must be positive")
    return Shape("text", (text, height, font))


def Rectangle2D(width, depth):
    """An XY rectangle with its lower-left corner at the origin."""
    return Shape("rectangle", (width, depth))


def RoundedRectangle2D(width, depth, radius):
    """One native rounded-rectangle profile for a named explicit Sketch.

    Four true circular sketch arcs; not a polygonal approximation.
    Current support is for Sketch.add(...), not standalone extrusion.
    """
    if pv(width) <= 0 or pv(depth) <= 0:
        raise ValueError("RoundedRectangle2D width and depth must be positive")
    if not 0 < pv(radius) * 2 < min(pv(width), pv(depth)):
        raise ValueError("RoundedRectangle2D radius must be below half the shorter side")
    return Shape("rounded_rectangle", (width, depth, radius))


def Circle2D(*, d=None, r=None):
    """An XY circle with diameter d or radius r."""
    if (d is None) == (r is None):
        raise ValueError("Circle2D requires exactly one of d= or r=")
    return Shape("circle", (d if d is not None else r * 2,))


def Polygon2D(points, *, plane="XY", ids=None, world=False):
    """A closed polygon. Rows may be (name, (u, v)) or plain (u, v).

    A name belongs to the vertex AND the segment starting at that vertex;
    sketch.line uses these names as segment IDs. On the XZ plane, world=True
    lets model code specify intuitive (x, z) instead of sketch-local (x, -z).
    """
    rows = tuple(points)
    named = [
        isinstance(row, (tuple, list)) and len(row) == 2
        and isinstance(row[0], str) and isinstance(row[1], (tuple, list))
        for row in rows
    ]
    if any(named):
        if not all(named):
            raise ValueError("all polygon vertices must be named, or none")
        if ids is not None:
            raise ValueError("named polygon points cannot also specify ids")
        ids = tuple(row[0] for row in rows)
        coordinates = tuple(tuple(row[1]) for row in rows)
    else:
        coordinates = tuple(tuple(p) for p in rows)
    if len(coordinates) < 3 or any(len(p) != 2 for p in coordinates):
        raise ValueError("Polygon2D requires at least three 2D points")
    if plane not in ("XY", "XZ", "YZ"):
        raise ValueError("unsupported sketch plane")
    if world:
        if plane != "XZ":
            raise ValueError("world=True currently supports only plane='XZ'")
        coordinates = tuple((x, -z) for x, z in coordinates)
    if ids is not None:
        if isinstance(ids, (str, bytes)) or not isinstance(ids, (tuple, list)):
            raise ValueError("polygon ids must be a sequence of segment names")
        if len(ids) != len(coordinates):
            raise ValueError("closed polygon needs exactly one id per segment")
        if any(not isinstance(tag, str) or not tag or
               not tag[0].isalpha() or
               not all(c.isalnum() or c == "_" for c in tag)
               for tag in ids):
            raise ValueError("polygon ids must be non-empty alphanumeric identifiers")
        if len(set(ids)) != len(ids):
            raise ValueError("polygon ids must be unique")
        ids = tuple(ids)
    return Shape("polygon", (coordinates, plane, ids))


def Box(length, width, thickness):
    return Shape("box", (length, width, thickness))


def Sphere(radius):
    return Shape("sphere", (radius,))


def Cylinder(*, d, h):
    """A cylinder based at z=0; use .at(x, y, z) for placement."""
    return Shape("cylinder", (h, d))


def Hole(*, d, depth=Depth.THROUGH_ALL, direction=None,
         countersink_d=None, countersink_angle=90, countersink_recess=0):
    """Hole intent, optionally directional and countersunk.

    Simple attached holes keep the sketch/cut history used by existing SCPF
    models. Directional or countersunk holes use SolidCraft's native Hole
    feature when explicitly positioned with .at().
    """
    if pv(d) <= 0:
        raise ValueError("hole diameter must be positive")
    if depth is not Depth.THROUGH_ALL and pv(depth) <= 0:
        raise ValueError("hole depth must be positive or Depth.THROUGH_ALL")
    if direction is not None:
        direction = tuple(direction)
        if len(direction) != 3:
            raise ValueError("Hole direction must be a 3D direction")
        concrete = [pv(v) for v in direction]
        if not all(isfinite(v) for v in concrete) or concrete == [0, 0, 0]:
            raise ValueError("Hole direction must be a finite non-zero direction")
    if countersink_d is not None:
        if pv(countersink_d) <= pv(d):
            raise ValueError("countersink diameter must be larger than hole diameter")
        angle = pv(countersink_angle)
        if not isfinite(angle) or angle <= 0 or angle >= 180:
            raise ValueError("countersink angle must be between 0 and 180 degrees")
        if pv(countersink_recess) < 0:
            raise ValueError("countersink recess cannot be negative")
    elif pv(countersink_recess) != 0:
        raise ValueError("countersink recess requires countersink_d")
    return Shape(
        "hole",
        (
            d, depth, direction, countersink_d, countersink_angle,
            countersink_recess,
        ),
    )


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
    from .history import History, active_history
    history = active_history()
    return Shape(
        "boss",
        (d, h, hole_d, direction),
        None if history is History.AUTO else history,
    )


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
