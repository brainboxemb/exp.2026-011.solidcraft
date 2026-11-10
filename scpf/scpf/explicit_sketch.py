"""Experimental explicit Sketch scope.

The scope owns editable 2D profiles. 3D operations are applied afterwards,
so authoring a sketch remains distinct from extruding/cutting it.
"""
from .core import Anchor, Depth, Direction, Shape, value_of


class Sketch:
    """Prototype named XY sketch attached to a supported parent face."""

    def __init__(self, *, name, on, parent=Anchor.TOP, plane=None, origin=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Sketch name must be non-empty")
        if not isinstance(on, Shape):
            raise TypeError("Sketch on= must be an existing Shape")
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
                value_of(coordinate)
        self.origin = tuple(origin) if origin is not None else None
        self.plane = plane
        self._profiles = []
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            if not self._profiles:
                raise ValueError("Sketch must contain at least one profile")
            self._closed = True
        return False

    def add(self, profile, *, offset=(0, 0)):
        if self._closed:
            raise ValueError("cannot add geometry after leaving the Sketch scope")
        if not isinstance(profile, Shape) or profile.kind not in ("circle", "rectangle", "text"):
            raise ValueError("Sketch supports Circle2D, Rectangle2D or Text2D profiles")
        if not isinstance(offset, (tuple, list)) or len(offset) != 2:
            raise ValueError("Sketch offset must be an (x, y) pair")
        # Numeric offsets are sufficient for the first syntax experiment.
        for value in offset:
            value_of(value)
        self._profiles.append((profile, tuple(offset)))
        return profile

    def extrude(self, distance, *, direction=Direction.POSITIVE):
        if not self._closed:
            raise ValueError("leave the Sketch scope before extruding it")
        if distance is not Depth.THROUGH_ALL and value_of(distance) <= 0:
            raise ValueError("Sketch extrusion distance must be positive or Depth.THROUGH_ALL")
        try:
            direction = Direction(direction)
        except ValueError as exc:
            raise ValueError("invalid Sketch extrusion direction") from exc
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
