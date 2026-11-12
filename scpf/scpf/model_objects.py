"""Internal reusable-model and assembly nodes.

User scripts keep ordinary class names such as Block() and Enclosure().
These nodes are the compiler-facing representation; users do not need to
construct Component or Occurrence objects explicitly.
"""
from dataclasses import dataclass, replace
from math import isfinite

from .core import Anchor, Axis, Shape, command_value, parameters_in, pv


@dataclass(frozen=True)
class ModelDefinition:
    """One reusable user-model definition before SolidCraft lowering."""

    class_name: str
    parameters: tuple[tuple[str, float], ...]
    shape: Shape
    fixed_inputs: tuple[tuple[str, float], ...] = ()
    external_parameters: tuple[tuple[str, float], ...] = ()
    input_bindings: tuple[tuple[str, str], ...] = ()

    @property
    def key(self):
        return (
            self.class_name,
            self.parameters,
            self.fixed_inputs,
            self.input_bindings,
        )


@dataclass(frozen=True)
class Attachment:
    """Associative face-to-face relationship between two model occurrences."""

    target: "ModelInstance"
    parent: Anchor
    child: Anchor
    offset: tuple[float, float]
    gap: object = 0


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

    width, depth, height = map(pv, (width, depth, height))
    x, y, z = map(pv, (x, y, z))
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
    rotation: tuple[tuple[float, float, float], float] | None = None
    group_name: str | None = None
    flattened_parameters: tuple[str, ...] = ()

    def group(self, name):
        """Keep this occurrence in a named native subassembly component."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("group name must be non-empty text")
        if self.group_name is not None and self.group_name != name:
            raise ValueError("an occurrence cannot belong to multiple groups")
        return replace(self, group_name=name)

    def copy(self):
        """Another occurrence of the same component, without rebuilding its shape.

        The copy starts at the same placement; move() it to a new position.
        The shared definition is compiled once, then SolidCraft receives
        occurrence.copy. Attachments are intentionally not inherited.
        """
        return replace(self, attachment=None)

    def move(self, x=0, y=0, z=0):
        """Translate this occurrence without changing shared component geometry.

        SolidCraft 0.30.1 occurrence translation is currently emitted as
        concrete coordinates. Remember any symbolic inputs so the root model
        can warn when a public parameter is only partly associative.
        """
        values = (x, y, z)
        symbolic = tuple(parameter.name for parameter in parameters_in(*values))
        flattened = tuple(dict.fromkeys(
            (*self.flattened_parameters, *symbolic)
        ))
        delta = tuple(pv(v) for v in values)
        if not all(isfinite(v) for v in delta):
            raise ValueError("model move() requires finite coordinates")
        current = self.translation
        return replace(
            self,
            translation=tuple(current[i] + delta[i] for i in range(3)),
            attachment=None,
            flattened_parameters=flattened,
        )

    def rotate(self, axis=(0, 0, 1), degrees=None):
        """Set this occurrence's absolute local-axis orientation in degrees.

        Named axis tokens allow concise calls such as rotate(X, 180) and
        rotate(Y, 90). The explicit tuple form remains supported:
        rotate(axis=(0, 1, 0), degrees=90).

        Rotates only the placement of the shared component definition.
        The pivot is the component's local origin; translation is preserved.
        One axis-angle orientation is supported, not chained Euler rotations.
        """
        if degrees is None:
            raise ValueError("model rotate() requires an angle in degrees")
        if isinstance(axis, Axis):
            axis = axis.value
        if isinstance(axis, str):
            named_axes = {
                "X": (1, 0, 0),
                "Y": (0, 1, 0),
                "Z": (0, 0, 1),
            }
            try:
                axis = named_axes[axis]
            except KeyError as exc:
                raise ValueError("model rotate() named axis must be X, Y or Z") from exc
        if (not isinstance(axis, (tuple, list)) or len(axis) != 3):
            raise ValueError("model rotate() axis must be X, Y, Z or an XYZ triple")
        symbolic = tuple(
            parameter.name
            for parameter in parameters_in(*axis, degrees)
        )
        flattened = tuple(dict.fromkeys(
            (*self.flattened_parameters, *symbolic)
        ))
        try:
            values = tuple(float(pv(value)) for value in axis)
            angle = float(pv(degrees))
        except (TypeError, ValueError) as exc:
            raise ValueError("model rotate() requires numeric axis and degrees") from exc
        if not all(isfinite(v) for v in (*values, angle)):
            raise ValueError("model rotate() requires finite coordinates and angle")
        if sum(v * v for v in values) <= 0:
            raise ValueError("model rotate() axis must be non-zero")
        return replace(
            self,
            rotation=(values, angle),
            attachment=None,
            flattened_parameters=flattened,
        )

    def attach(self, target, *, parent=Anchor.RIGHT, child=Anchor.LEFT,
               offset=(0, 0), gap=0):
        """Match one component face to another with a native rigid joint.

        A symbolic gap is preserved as a SolidCraft joint expression, so
        changing its parameter in the saved design re-solves placement.
        """
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
        face_offset = tuple(pv(v) for v in offset)
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
        try:
            gap_value = pv(gap)
        except TypeError as exc:
            raise ValueError("component attach gap must be a CAD dimension") from exc
        if not isfinite(gap_value):
            raise ValueError("component attach gap must be finite")

        return replace(
            self,
            translation=translation,
            attachment=Attachment(
                target=target,
                parent=parent,
                child=child,
                offset=face_offset,
                gap=gap,
            ),
        )

    def __add__(self, other):
        return Assembly((self,)) + other

    __or__ = __add__


@dataclass(frozen=True)
class Assembly:
    """Ordered collection of reusable model occurrences."""

    instances: tuple[ModelInstance, ...]

    def group(self, name):
        """Wrap these occurrences in a real nested native component."""
        return Assembly(tuple(instance.group(name) for instance in self.instances))

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
