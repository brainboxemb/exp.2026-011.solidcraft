"""Internal reusable-model and assembly nodes.

User scripts keep ordinary class names such as Block() and Enclosure().
These nodes are the compiler-facing representation; users do not need to
construct Component or Occurrence objects explicitly.
"""
from dataclasses import dataclass, replace
from math import isfinite

from .core import Shape, value_of


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
class ModelInstance:
    """One placed occurrence of a reusable model definition."""

    definition: ModelDefinition
    translation: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def move(self, x=0, y=0, z=0):
        """Translate this occurrence without changing shared component geometry."""
        delta = tuple(value_of(v) for v in (x, y, z))
        if not all(isfinite(v) for v in delta):
            raise ValueError("model move() requires finite coordinates")
        current = self.translation
        return replace(
            self,
            translation=tuple(current[i] + delta[i] for i in range(3)),
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
