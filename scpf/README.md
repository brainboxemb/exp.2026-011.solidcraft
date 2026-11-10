# SCPF — SolidCraft Python Forge (proof of concept)

SCPF describes CAD models in ordinary Python and compiles them to
**native SolidCraft command JSON**. It is not a second geometry engine,
not a SolidCraft MCP implementation, and does not replace SolidCraft's
own MCP/RPC control interface.

The objective is a compact model language with useful CSG and CAD features:
readability first, fewer nested operations than OpenSCAD, while preserving
native SolidCraft feature history when possible.

## Model objects

The preferred SCPF style is a reusable Python dataclass. Numeric fields
are CAD parameters, and `build()` constructs the model. The last Shape
expression in `build()` is the result: no `return`, `show()` or `main()`.

```python
@dataclass
class Plate:
    length: float = 100
    width: float = 60
    thickness: float = 10

    def build(self):
        body = Box(self.length, self.width, self.thickness).fillet(2)
        holes = Cylinder(d=8, h=self.thickness).pattern(x=70, y=30)
        body - holes

Plate()
```

SCPF makes `dataclass` available without an import. It constructs the
Python object normally (including `__post_init__` validation), promotes
numeric model fields to SolidCraft parameters, and calls `build()`.
`@dataclass(frozen=True)` is also supported. The last-expression behavior
is an SCPF convention, not normal Python behavior.

Three CAD examples:
- [Plate](../examples/plate/scpf/model.py): rounded box with holes.
- [CsgCube](../examples/csg-cube/scpf/model.py): intersect and cut solids.
- [Bracket](../examples/bracket/scpf/model.py): polygon extrusion, fillet and holes.

Older function models with an implicit final Shape expression remain
supported. Ordinary helpers still use standard Python semantics.
## Positioning

CSG primitives and complete CSG combinations can be repositioned in mm:

```python
def MovedCube(size=50):
    body = Sphere(size / 1.5) & Box(size, size, size)
    return body.move(x=10, y=20, z=30)

MovedCube()
```

The move applies to all primitives in the CSG tree, including
subtractive cylinders. It is emitted as SolidCraft coordinates, not an
approximate mesh transformation. At present, `.move()` on
feature-based Plate bodies is deliberately rejected.

## Parameters

The runner reads the final model class constructor signature using
`inspect.signature`. Numerical fields become named CAD parameters,
including arguments explicitly overridden by the final call:

```python
Plate(120, 80, 12)
```

SCPF preserves symbolic expressions such as `size / 1.5` in emitted JSON.
For the supported box, parameters `length`, `width` and `thickness`
become native SolidCraft parameters and remain editable in native history.
This is **not** automatic tracking of arbitrary Python calculations.
The first version supports simple parameter arithmetic and predefined
operations only.

Plain numbers mean millimetres. SCPF scripts are real Python: only execute
trusted model files.

## Run and inspect the Bracket

Run commands below from the repository root in PowerShell. The Python
environment must be active, or install the package with
`python -m pip install -e ./scpf`. Alternatively set the package path:

```powershell
$env:PYTHONPATH = "scpf"
```

**1. Generate and inspect the native command JSON** (does not open the GUI):

```powershell
python -m scpf examples/bracket/scpf/model.py --out output/examples/bracket/scpf/solidcraft.json
code output/examples/bracket/scpf/solidcraft.json
```

The `--out` path is under `output/`, which is excluded by Git. The
canonical comparison fixture is retained at
`examples/bracket/scpf/solidcraft.json`. The uploaded original is at
`examples/bracket/source/bracket.json`.

**Replay an existing SolidCraft command JSON directly** (no conversion):

```powershell
python -m scpf replay examples/bracket/source/bracket.json
```

This sends the JSON commands **unchanged** to the open SolidCraft app.
You may also pass `--connect` and an explicit port, but normally neither
is needed. The original Bracket JSON starts with `parameters.change`;
create `width` and `thickness` in the current design first. For a
**new empty document** use the standalone SCPF-generated JSON instead:

```powershell
python -m scpf replay examples/bracket/scpf/solidcraft.json
```

**2. Execute in the currently running SolidCraft GUI** (live):

```powershell
python -m scpf examples/bracket/scpf/model.py --connect
```

Start with a **new empty document** and enable external Assistant control
inside SolidCraft. `--connect` executes a batch directly and **does not
write a command JSON file**. The default connection uses the local GUI
control port and authentication token. The existing document is modified;
the batch requests rollback if a step fails. Close/recreate the document
before repeating a complete standalone model, otherwise `parameters.add`
may fail with an already-existing `width` or `thickness` parameter.
A local fake control server is used in CI; the real GUI is tested manually.

**3. Execute without connecting to a running GUI**:

```powershell
python -m scpf examples/bracket/scpf/model.py --out output/examples/bracket/scpf/solidcraft.json
solidcraft-cli run output/examples/bracket/scpf/solidcraft.json --param-check strict --save output/bracket.sc
```

Open the resulting `output/bracket.sc` in the SolidCraft GUI. Or use
the helper `./scripts/open-solidcraft-json.ps1` on Windows with `-Script`
set to the generated command file.

**4. Run regression tests**:

```powershell
python -m unittest discover -s scpf/tests -v
```

The source command JSON uses `parameters.change` because it assumes
`width` and `thickness` already exist in an open SolidCraft design.
SCPF produces a **standalone command plan** starting with
`parameters.add`; those two differences are intentional. The remaining
geometry operations (XZ sketch, extrusion, fillet, two XY holes and cut)
are checked against the uploaded source. SolidCraft maps XZ sketch
vertical coordinates into **negative world Z**, so the bracket's fillet
edge is at `[40, -30, -6]` and the hole cut uses
`direction: "negative"`. An earlier SCPF version incorrectly used
positive Z; this has been corrected following a real GUI error.


## Results website

The CAD results website is built by
`scripts/ci/build-results.py` and published from GitHub Actions to
GitHub Pages, with a PR-specific preview. It contains separate pages
for Plate, CsgCube and Bracket, code, command JSON, construction
stages and schematic illustrations. Native CAD screenshots are only
included if their verification metadata matches the exact source
commit; unverified previews are explicitly labelled.

## Current limits

- Supported primitives: box (feature model), cube, sphere, cylinder.
- CSG: intersection, union, difference, and oriented cylinder cutters.
- Feature model: box, vertical-edge fillet, rectangular pattern of four
  through-cylinder cutters. These are exact native SolidCraft features
  after running the resulting commands.
- This is an explicit, narrow translation layer: arbitrary Python code
  can execute, but not every shape composition can be compiled into
  SolidCraft commands yet.
- Positioning: `Shape.move(x=..., y=..., z=...)` now translates
  native CSG primitives and composite CSG shapes without changing dimensions.
  More general positioning (including feature-based box placement),
  rotations, face/edge selectors, arbitrary patterns, richer dimensional
  arithmetic and model reuse are future work.
- SolidCraft, not SCPF, remains responsible for topology, solving and geometry.

## Sample Plate reconstruction

The source document [Sample Plate](../examples/sample-plate/source/Sample%20Plate.json)
contains an editable SolidCraft **design history**, not command JSON.
The [SCPF class](../examples/sample-plate/scpf/model.py) describes the base,
mounting holes, joined boss, and bore with the same object-level operations:
`Rectangle2D`, `Cylinder`, and the native `Hole` feature. The adapter creates
a sketch internally for the base and the boss, while all three holes compile
to native `solid.hole`. A `Hole` is added to the model using `+`, even
though the resulting CAD feature removes material.

This intentionally differs from the original saved file's **four sketches and
nine features**. The source retains its original sketch-based cut history;
the generated design instead contains `Base`, two mounting Hole features,
`Boss`, and one bore Hole feature. Geometry and parameter edits must be
verified independently rather than claiming identical feature histories.

```powershell
$env:PYTHONPATH = "scpf"
python -m scpf examples/sample-plate/scpf/model.py --out output/examples/sample-plate/scpf/solidcraft.json
python -m scpf examples/sample-plate/scpf/model.py --connect
```

The live command requires a new empty SolidCraft design; the generated
command plan creates its own parameters. Native validation is required
before accepting this reconstruction as geometrically equivalent.

## SCPF API cheatsheet

The generated results website includes a `/cheatsheet/` page.
2D profiles have an explicit suffix: `Rectangle2D`, `Circle2D` and
`Polygon2D`. 3D solids use plain names: `Box`, `Cylinder`
and `Sphere`. The direct `Cylinder(d=..., h=...)` starts at its lower face. The
`pattern()` and `orient()` helpers center generated cutter cylinders on
their respective axes, preserving the Plate and CsgCube command fixtures.
The old positional constructor and 3D-suffixed aliases are not supported.

## Edge selection

Use `Edges.VERTICAL` for automatic selection of vertical edges on supported
rectangular bodies, or supply a list of explicit 3D edge points for a
specific edge. This is intentionally distinct from the planned object
attachment anchors (`Anchor.TOP`, etc.). Strings such as
`edges="vertical"` are no longer part of the SCPF API.

## Relative anchors and symmetric patterns (experimental)

For a rectangular XY plate, placement can reference the plate rather than
hard-coded world coordinates:

```python
plate = Rectangle2D(100, 60).extrude(10)
holes = Cylinder(d=8, h=12).pattern(
    count=2, spacing=40, axis=Axis.Y
).on(plate, Anchor.CENTER)
plate - holes
```

`on()` aligns the child center with the parent anchor.
`attach(target, parent=Anchor.TOP, child=Anchor.BOTTOM)` connects two
explicit anchors. `offset=(dx, dy)` is measured along the local XY axes.
Currently supported: Rectangle2D extrusion base; `Anchor.CENTER`,
`Anchor.TOP`, `Anchor.BOTTOM`; and XY linear patterns of cylinders.

For `Anchor.TOP` and `Anchor.BOTTOM`, the native adapter now emits
`references` with two perpendicular straight edge picks and parametric
distances. The accompanying `base` or `position` is numeric because
SolidCraft explicitly requires numeric coordinates when using references.
The initial edge pick points are not promises of stable topology across all
changes: only a simple rectangular XY base is supported, and native
save/reopen/parameter-edit qualification is required.

`Hole(d=8, depth=Depth.THROUGH_ALL)` describes a native `solid.hole`
feature, distinct from a cutting Cylinder. Use it with `on()` and add
it to the parent as `plate + hole`. The plus adds a CAD feature, not material:
the native `solid.hole` operation removes material. Older `plate - hole`
scripts remain supported for compatibility. `Fillet` remains a modifier method on solids.
More general attachments remain tracked in issue #5.

## Sketches versus direct features

SCPF currently handles sketches **implicitly**. `Rectangle2D(...).extrude(...)`
compiles to native `sketch.create`, rectangle curves, `sketch.finish`,
and `solid.extrude`. Likewise, `Circle2D` profiles in an extruded
cut create a native sketch and subtractive extrusion. Those sketches
are preserved in SolidCraft's feature history, where they can be edited.

By contrast, `Hole(...).on(plate, Anchor.TOP)` is a **direct native Hole
feature** and emits `solid.hole` with two edge references; it does not
require a sketch. This is useful for one or a few holes positioned by
reference edges. The `pattern(count=2, spacing=..., axis=...)` form
currently expands to two individual native Hole features, **not** to one
constraint-driven point sketch or one native pattern feature.

A named, reusable SCPF `Sketch` object with construction lines,
constraints, point layouts, and workplanes attached to faces is planned
in [issue #9](https://github.com/brainboxemb/exp.2026-011.solidcraft/issues/9).
For now, do **not** interpret `Circle2D` as a fully constrained sketch.
This deliberate distinction keeps the current anchor work separate from
a larger sketch/solver abstraction.
