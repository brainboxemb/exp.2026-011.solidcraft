# 07 — µcad inspiration: declarative part definitions and units

The [µcad source on Codeberg](https://codeberg.org/microcad/microcad/)
is a parametric CAD *language*. We are **not** using it as a geometry
engine or adopting its parser; SolidCraft remains our only CAD engine.

**Source provenance:** The current Codeberg repository could not be fetched
automatically. This note is based on the project's **older GitHub
repository**, which explicitly says it moved to Codeberg:
[README](https://github.com/Rustfahrtagentur/microcad),
[concepts](https://github.com/Rustfahrtagentur/microcad/blob/main/doc/CONCEPTS.md),
[LEGO example](https://github.com/Rustfahrtagentur/microcad/blob/main/examples/lego_brick.%C2%B5cad).
We do not assume that the current Codeberg code is identical.

## Four lessons worth keeping

### 1. Define a part, not a sequence of protocol requests

The historical µcad Hello World expresses a *named part* with size
and subtractive solids:

```text
part CsgCube(size: Length) {
    body = Sphere(r = size / 1.5) & Cube(size);
    holes = Cylinder(h = size, d = size / 1.5).orient([X,Y,Z]);
    body - holes;
}
CsgCube(50mm);
```

That supports our goal: callers should see Part, Hole and Fillet,
never `sketch.finish` or command IDs.

The example's `.orient([X,Y,Z])` is µcad syntax, not an SCPF API target.
Forge deliberately does not copy that Cylinder-specific multi-axis shortcut.
If richer solid orientation is needed, it should come from a general transform
or direction model shared by shapes.

### 2. Keep dimensions and parameter expressions explicit

µcad uses typed quantities such as `50mm`. SCPF currently uses Python
numbers in millimetres and binds dataclass fields to named SolidCraft
parameters. We have not introduced a full physical-unit type system.

```python
@dataclass
class Plate:
    width: float = 100
    thickness: float = 10

    def build(self):
        Rectangle2D(self.width, 60).extrude(self.thickness)

Plate()
```

### 3. Separate Part, Sketch and Operation as domain concepts

The µcad concepts distinguish 2D sketches, 3D parts and operations
on them. That suggests separate objects for reusable `Sketch` /
`PartDefinition`, ordered `Feature` operations, workplanes and
later assemblies.

A **domain Sketch** is not a call to the SolidCraft command
`sketch.create`: it describes a 2D object and local coordinate space.
The SolidCraft adapter decides how to create and finish an actual sketch.

### 4. Separate definition from CAD execution

Borrow the *principle* of µcad's definition/evaluation separation,
without creating a new language or geometry kernel:

```text
Python objects / named parameters (declarative CAD intent)
         ↓
Domain checks, dimensions and named references
         ↓
SolidCraft adapter (expand one feature into multiple commands)
         ↓
Script / GUI-control / MCP transport
         ↓
SolidCraft engine (geometry and native feature timeline)
```

This makes unit tests and readable model composition possible with
no SolidCraft installation. It does not prove a real solid is generated
correctly.

## CadQuery, vcad, µcad and PythonSCAD have complementary roles

| Design reference | Useful idea for our SolidCraft CAD API |
|---|---|
| [CadQuery](https://cadquery.readthedocs.io/en/latest/examples.html) | Context-aware face/edge selection, workplanes, construction geometry |
| [vcad](https://docs.rs/vcad/latest/vcad/) | Compact fluent Rust model construction |
| [µcad](https://codeberg.org/microcad/microcad/) | Declarative named parts/sketches/operations and typed units |
| PythonSCAD | Lightweight object-style scripting and direct CSG operators |

All four are **interface inspirations only**. None of their geometry
engines is in our implementation.

## Validation and next step

Qualify Python-native Hole and attachment features with SolidCraft
before introducing more abstractions. The difficult next problem is reliable, CAD-semantic
face and edge selection against SolidCraft's actual topology, and
preserving named parameters in an editable native design.
