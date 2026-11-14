"""Experimental explicit Sketch scope.

The scope owns editable 2D profiles. 3D operations are applied afterwards,
so authoring a sketch remains distinct from extruding/cutting it.
"""
from contextvars import ContextVar

from .core import Anchor, Depth, Direction, Shape, pv

_ACTIVE_SKETCH = ContextVar("scpf_active_sketch", default=None)


def register_profile(profile):
    """Capture authored 2D geometry only while an explicit Sketch is active."""
    sketch = _ACTIVE_SKETCH.get()
    if sketch is not None:
        sketch.add(profile)
    return profile


class Sketch:
    """Prototype named XY sketch attached to a supported parent face."""

    def __init__(self, *, name="Profile", on=None, parent=Anchor.TOP, plane=None, origin=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Sketch name must be non-empty")
        if on is not None and not isinstance(on, Shape):
            raise TypeError("Sketch on= must be an existing Shape")
        if on is None and plane is None:
            plane = "XY"
        try:
            parent = Anchor(parent)
        except ValueError as exc:
            raise ValueError("Sketch parent must be an Anchor") from exc
        if plane is not None and plane not in ("XY", "XZ", "YZ"):
            raise ValueError("Sketch plane must be XY, XZ or YZ")
        self.name = name
        self.on = on
        self.parent = parent
        if origin is not None:
            if plane not in ("XY", "XZ", "YZ"):
                raise ValueError("Sketch origin requires an explicit XY, XZ or YZ plane")
            if not isinstance(origin, (list, tuple)) or len(origin) != 3:
                raise ValueError("Sketch origin must be a 3D coordinate")
            for coordinate in origin:
                pv(coordinate)
        self.origin = tuple(origin) if origin is not None else None
        self.plane = plane
        self._profiles = []
        self._closed = False
        self._token = None

    def __enter__(self):
        if self._closed or self._token is not None:
            raise ValueError("Sketch scope cannot be re-entered")
        self._token = _ACTIVE_SKETCH.set(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        _ACTIVE_SKETCH.reset(self._token)
        self._token = None
        if exc_type is None:
            if not self._profiles:
                raise ValueError("Sketch must contain at least one profile")
            self._closed = True
        return False

    def add(self, profile, *, offset=(0, 0)):
        if self._closed:
            raise ValueError("cannot add geometry after leaving the Sketch scope")
        if not isinstance(profile, Shape) or profile.kind not in ("circle", "rectangle", "rounded_rectangle", "text", "polygon"):
            raise ValueError("Sketch supports Circle2D, Rectangle2D, Polygon2D, RoundedRectangle2D or Text2D profiles")
        if not isinstance(offset, (tuple, list)) or len(offset) != 2:
            raise ValueError("Sketch offset must be an (x, y) pair")
        # Numeric offsets are sufficient for the first syntax experiment.
        for value in offset:
            pv(value)
        # An explicitly added profile may already have been captured by its
        # constructor inside the scope. Replace its automatic placement.
        self._profiles = [row for row in self._profiles if row[0] is not profile]
        self._profiles.append((profile, tuple(offset)))
        return profile

    def extrude(self, distance, *, direction=Direction.POSITIVE):
        if not self._closed:
            raise ValueError("leave the Sketch scope before extruding it")
        if distance is not Depth.THROUGH_ALL and pv(distance) <= 0:
            raise ValueError("Sketch extrusion distance must be positive or Depth.THROUGH_ALL")
        try:
            direction = Direction(direction)
        except ValueError as exc:
            raise ValueError("invalid Sketch extrusion direction") from exc
        if self.on is None:
            if distance is Depth.THROUGH_ALL:
                raise ValueError("standalone Sketch requires a finite extrusion distance")
            return Shape(
                "sketch_base_extrusion",
                (self.name, self.plane, self.origin, tuple(self._profiles), distance, direction.value),
            )
        return Shape(
            "explicit_sketch_extrusion",
            (
                self.name,
                self.on,
                self.parent,
                (self.plane, self.origin),
                tuple(self._profiles),
                distance,
                direction.value,
            ),
        )
