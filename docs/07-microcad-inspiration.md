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

### 2. Give physical quantities explicit types and units

µcad uses `Length` and values like `50mm`. Our Rust PoP now also
has a deliberately minimal domain type:

```rust
use solidcraft_facade_poc::cad::{Length, Part, Hole};

let part = Part::box_with_units(
    Length::mm(100.0), Length::inches(2.0), Length::mm(10.0)
)?;
let hole = Hole::with_units(
    Length::mm(0.0), Length::mm(0.0), Length::mm(8.0)
)?;
```

These typed calls normalize to millimeters *in the CAD domain* and
reject invalid sizes in the downstream constructors. They are an optional
alternative to the first PoP's f64-in-mm shortcut, not yet a complete
physical quantities system. Angle, area, volume and expressions remain
future work.

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
Rust Part / Sketch / parameters (declarative CAD intent)
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

## CadQuery, vcad and µcad have complementary roles

| Design reference | Useful idea for our SolidCraft CAD API |
|---|---|
| [CadQuery](https://cadquery.readthedocs.io/en/latest/examples.html) | Context-aware face/edge selection, workplanes, construction geometry |
| [vcad](https://docs.rs/vcad/latest/vcad/) | Compact fluent Rust model construction |
| [µcad](https://codeberg.org/microcad/microcad/) | Declarative named parts/sketches/operations and typed units |

All three are **interface inspirations only**. None of their geometry
engines is in our implementation.

## Validation and next step

Check typed length conversion in Rust CI, then **qualify our existing
semantic box/fillet/holes fixture on SolidCraft 0.30.1** before adding
more abstraction. The difficult next problem is reliable, CAD-semantic
face and edge selection against SolidCraft's actual topology, and
preserving named parameters in an editable native design.
