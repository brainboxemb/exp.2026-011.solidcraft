"""Internal reusable-model and assembly nodes.

User scripts keep ordinary class names such as Block() and Enclosure().
These nodes are the compiler-facing representation; users do not need to
construct Component or Occurrence objects explicitly.
"""
from dataclasses import dataclass, replace
from math import isfinite

from .core import Anchor, Shape, value_of


@dataclass(frozen=True)
class ModelDefinition:
    """One reusable user-model definition before SolidCraft lowering."""

    class_name: str
    parameters: tuple[tuple[str, float], ...]
    shape: Shape

    @property
    def key(self):
        return self.class_name, self.parameters


@dataclass(frozen=True)
class Attachment:
    """Associative face-to-face relationship between two model occurrences."""

    target: "ModelInstance"
    parent: Anchor
    child: Anchor
    offset: tuple[float, float]


def _rectangular_bounds(instance):
    """Return local axis-aligned bounds for the first component experiment."""
    from .placement import _base_rectangle

    try:
        (width, depth), (x, y, z), height = _base_rectangle(
            instance.definition.shape
        )
    except ValueError as exc:
        raise ValueError(
            "component attach currently requires a rectangular model"
        ) from exc

    width, depth, height = map(value_of, (width, depth, height))
    x, y, z = map(value_of, (x, y, z))
    return (
        (x, x + width),
        (y, y + depth),
        (z, z + height),
    )


def _anchor_point(instance, anchor):
    """Local face-centre point for one reusable component."""
    bounds = _rectangular_bounds(instance)
    (xmin, xmax), (ymin, ymax), (zmin, zmax) = bounds
    xmid = (xmin + xmax) / 2
    ymid = (ymin + ymax) / 2
    zmid = (zmin + zmax) / 2
    points = {
        Anchor.CENTER: (xmid, ymid, zmid),
        Anchor.LEFT: (xmin, ymid, zmid),
        Anchor.RIGHT: (xmax, ymid, zmid),
        Anchor.FRONT: (xmid, ymin, zmid),
        Anchor.BACK: (xmid, ymax, zmid),
        Anchor.BOTTOM: (xmid, ymid, zmin),
        Anchor.TOP: (xmid, ymid, zmax),
    }
    if anchor not in points:
        raise ValueError("Anchor.INNER_BOTTOM is not an assembly face anchor")
    return points[anchor]


def _face_offset(anchor, offset):
    """Map a two-value face offset into XYZ."""
    u, v = offset
    if anchor in (Anchor.LEFT, Anchor.RIGHT):
        return (0.0, u, v)
    if anchor in (Anchor.FRONT, Anchor.BACK):
        return (u, 0.0, v)
    if anchor in (Anchor.TOP, Anchor.BOTTOM):
        return (u, v, 0.0)
    if anchor is Anchor.CENTER:
        return (u, v, 0.0)
    raise ValueError("unsupported assembly anchor")


@dataclass(frozen=True)
class ModelInstance:
    """One placed occurrence of a reusable model definition."""

    definition: ModelDefinition
    translation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    attachment: Attachment | None = None

    def move(self, x=0, y=0, z=0):
        """Translate this occurrence without changing shared component geometry."""
        delta = tuple(value_of(v) for v in (x, y, z))
        if not all(isfinite(v) for v in delta):
            raise ValueError("model move() requires finite coordinates")
        current = self.translation
        return replace(
            self,
            translation=tuple(current[i] + delta[i] for i in range(3)),
            attachment=None,
        )

    def attach(self, target, *, parent=Anchor.RIGHT, child=Anchor.LEFT,
               offset=(0, 0)):
        """Match one component face to another and retain a rigid relationship."""
        if not isinstance(target, ModelInstance):
            raise TypeError("component attach target must be another model object")
        try:
            parent = Anchor(parent)
            child = Anchor(child)
        except ValueError as exc:
            raise ValueError("component attach requires Anchor values") from exc
        if parent is Anchor.INNER_BOTTOM or child is Anchor.INNER_BOTTOM:
            raise ValueError("Anchor.INNER_BOTTOM is not an assembly face anchor")
        if not isinstance(offset, (tuple, list)) or len(offset) != 2:
            raise ValueError("component attach offset must be an (u, v) pair")
        face_offset = tuple(value_of(v) for v in offset)
        if not all(isfinite(v) for v in face_offset):
            raise ValueError("component attach offset must be finite")
        if any(face_offset):
            raise ValueError(
                "component attach offset is not implemented associatively yet"
            )

        target_local = _anchor_point(target, parent)
        child_local = _anchor_point(self, child)
        tangent = _face_offset(parent, face_offset)
        target_world = tuple(
            target_local[i] + target.translation[i] + tangent[i]
            for i in range(3)
        )
        translation = tuple(
            target_world[i] - child_local[i]
            for i in range(3)
        )
        return replace(
            self,
            translation=translation,
            attachment=Attachment(
                target=target,
                parent=parent,
                child=child,
                offset=face_offset,
            ),
        )

    def __add__(self, other):
        return Assembly((self,)) + other

    __or__ = __add__


@dataclass(frozen=True)
class Assembly:
    """Ordered collection of reusable model occurrences."""

    instances: tuple[ModelInstance, ...]

    def __post_init__(self):
        if not self.instances:
            raise ValueError("assembly must contain at least one model instance")
        if not all(isinstance(item, ModelInstance) for item in self.instances):
            raise TypeError("assembly items must be model instances")

    def __add__(self, other):
        if isinstance(other, ModelInstance):
            return Assembly(self.instances + (other,))
        if isinstance(other, Assembly):
            return Assembly(self.instances + other.instances)
        return NotImplemented

    __or__ = __add__
