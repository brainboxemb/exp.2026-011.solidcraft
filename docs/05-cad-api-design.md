# 05 — Designing a real CAD API (CadQuery + vcad as references)

## Why we are doing this

In the first prototype, a user had to call `sketch.create`,
`sketch.finish` and `solid.extrude`. That was a nicer *command wrapper*,
but it did not let the user focus on **what the part is**.

We want the same difference seen between these two levels:

### Lower level: direct SolidCraft commands (existing Python scraftpybind)

```python
solidcraft.sketch.create(plane="XY", name="Plate")
outline = solidcraft.sketch.rectangle_center(center=(0, 0), corner=(50, 30))
solidcraft.sketch.circle_center(center=(0, 0), diameter=20)
solidcraft.sketch.finish()
solidcraft.solid.extrude(
    distance=10, profiles=[{"curves": outline["curves"]}], body_name="Plate"
)
```

Source: [scraftcnc Python example](https://github.com/waynegramlich/scraftcnc/blob/main/scraftcnc/pybind/examples/plate_with_holes.py).

### Higher level: the kind of design code we want

```rust
let plate = Part::box3d(100.0, 60.0, 10.0)?
    .named("Plate")
    .edges(Edges::OuterVertical).fillet(2.0)?
    .through_holes(&holes)?;

solidcraft.build(&plate)?;
```

This second example corresponds to **real code in**
[`rust-facade/src/bin/cad_plate.rs`](../rust-facade/src/bin/cad_plate.rs),
using the `SolidCraftAdapter` under the variable name `solidcraft`
for illustration. The linked file gives its precise imports and setup.

## What CadQuery teaches us

Read the official [Workplane guide](https://cadquery.readthedocs.io/en/stable/workplane.html)
and [examples](https://cadquery.readthedocs.io/en/latest/examples.html).

### 1 — Select geometry by meaning, not by coordinates

CadQuery uses methods like `faces(">Z")` and `edges("|Z")`.
The reader need not know the indices of the top face or the four
vertical edges. For example:

```python
import cadquery as cq

plate = cq.Workplane("XY").box(100, 60, 10)
plate = plate.edges("|Z").fillet(2)
```

Our design should use *typed* selectors rather than copy CadQuery's
string syntax blindly. Initially `Edges::OuterVertical` means only
the four original upright edges of the base box. **It is not equivalent
to CadQuery's fully generic `"|Z"` selector** when additional features
are present. A general selector requires inspecting SolidCraft's
actual topology and resolving the correct edge picks.

### 2 — Model from meaningful workplanes

CadQuery can choose a top face, open a local workplane, place a pattern
there, and drill holes:

```python
plate = (cq.Workplane("XY").box(100, 60, 10)
    .faces(">Z").workplane()
    .rect(80, 40, forConstruction=True)
    .vertices().hole(8))
```

An eventual Rust API could look like (proposed; **not implemented**):

```rust
part.on(Faces::Top)?
    .workplane()
    .rectangle(80.0, 40.0).construction()
    .vertices().hole(8.0)?
```

This implies actual face selection, local coordinates, point placement,
construction geometry, and feature references in the adapter. It is a
larger task than sending a single `solid.hole` command.

### 3 — Chain methods but preserve readable feature history

CadQuery returns a new `Workplane` object from most operations and
supports context objects, tags and earlier steps in a modeling chain.
We can borrow its **readable chaining** without duplicating the entire
CadQuery stack/context implementation. Our first `Part` stores a base
and an *ordered feature list*. That order is explicit and testable.

Later investigate named sketches, workplanes and stable references
rather than relying permanently on geometrical edge pick points.

### 4 — A hole is a CAD operation, not a command name

Our `through_holes(&holes)` is one CAD intent. The SolidCraft adapter
creates a sketch on the plate's top, draws each circle, finishes it,
then extrudes negatively with `operation:"cut"`.
The user does not have to know or manage these intermediate steps.

## Four separate responsibilities

```text
Rust CAD domain (Part, Hole, Edges, ordered features)
   │  independent of SolidCraft/serde/JSON
   ▼
SolidCraft adapter (translate CAD intent into operations)
   │  knows sketches, feature order and edge-pick semantics
   ▼
CommandTransport (script now; GUI control/MCP later)
   │  serializes commands and propagates errors/results
   ▼
SolidCraft engine (only actual model geometry & history)
```

`vcad`'s Rust library is likewise a reference for **fluent API shape**,
**not** a second engine. `CadQuery` itself is not a dependency.

## Scope of this first implementation

**Implemented at source level:**
- `Part::box3d(length, width, height)`, centered about XY;
- `.named(...)`, `.edges(Edges::OuterVertical).fillet(radius)`;
- `.through_holes(&[Hole::at(x, y, diameter)?])`;
- dimensions validation, feature ordering, and domain tests;
- SolidCraft adapter tests checking expansion into multiple commands.

**Not yet qualified:**
- Rust compilation and tests in the target environment;
- actual SolidCraft CLI execution / STEP export;
- generic BRep face and edge selection, named topological handles;
- custom workplanes and construction geometry;
- native parametric edit and save/reopen;
- same domain API with GUI control port or headless MCP.

## Next qualification

First verify the fixture works in the installed SolidCraft version.
Then add a face selector and a local workplane: this is where CadQuery's
design adds the most value, but it must be backed by genuine SolidCraft
topology operations rather than guessed XYZ points.
