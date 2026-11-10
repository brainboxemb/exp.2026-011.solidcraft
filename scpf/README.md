# SCPF — SolidCraft Python Forge (proof of concept)

SCPF describes CAD models in ordinary Python and compiles them to
**native SolidCraft command JSON**. It is not a second geometry engine,
not a SolidCraft MCP implementation, and does not replace SolidCraft's
own MCP/RPC control interface.

The objective is a compact model language with useful CSG and CAD features:
readability first, fewer nested operations than OpenSCAD, while preserving
native SolidCraft feature history when possible.

## Model objects

The preferred SCPF style is a plain Python class. Numeric class fields are
CAD parameters, and `build()` constructs the model. The last Shape
expression in `build()` is the result: no `return`, `show()` or `main()`.

```python
class Plate:
    length = 100.0
    width = 60.0
    thickness = 10.0

    def build(self):
        body = Box(self.length, self.width, self.thickness)
        body = body.fillet(2, edges=Edges.VERTICAL)
        body

Plate()
```

SCPF promotes those numeric class fields to SolidCraft parameters and also
allows overrides such as `Plate(width=80.0)` without requiring a handwritten
`__init__`. Existing `@dataclass` models remain supported, including
`@dataclass(frozen=True)` and `__post_init__` validation. The
last-expression behavior is an SCPF convention, not normal Python behavior.

Five CAD examples:
- [Plate](../examples/plate/scpf/model.py): rounded box with holes.
- [CsgCube](../examples/csg-cube/scpf/model.py): intersect and cut solids.
- [Bracket](../examples/bracket/scpf/model.py): polygon extrusion, fillet and native Hole features.
- [Sample Plate](../examples/sample-plate/scpf/model.py): boss, bore, and mounting holes.
- [Plastic Enclosure](../examples/plastic-enclosure/scpf/model.py): shell, lip, snap fit, screw bosses and rest.

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

For a plain model class, numeric class fields become named CAD parameters in
declaration order. The final model call may override them by name or position:

```python
Plate(width=80.0)
Plate(120.0, 80.0, 12.0)
```

Dataclass models continue to use their normal constructor signature.

SCPF preserves symbolic expressions such as `size / 1.5` in emitted JSON.
For the supported box, parameters `length`, `width` and `thickness`
become native SolidCraft parameters and remain editable in native history.
This is **not** automatic tracking of arbitrary Python calculations.
The first version supports simple parameter arithmetic and predefined
operations only.

Plain numbers mean millimetres. SCPF scripts are real Python: only execute
trusted model files.

## Run and inspect the Bracket

Run commands below from the repository root in PowerShell. This is an
experiment repository, so the normal local-development workflow runs SCPF
directly from the checkout rather than installing it as a package:

```powershell
$env:PYTHONPATH = "scpf"
```

An editable pip install is optional and is not required for normal development.

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
for all SCPF examples, with code, command JSON, construction
stages and schematic illustrations. Native CAD screenshots are only
included if their verification metadata matches the exact source
commit; unverified previews are explicitly labelled.

## Code organization

The compiler is divided by **responsibility**, not by example model:

- `core.py`: user-facing Python shapes, parameters, anchors, operations.
- `compiler.py`: small entry point and parameter collection.
- `sketches.py`: native sketch and base-extrusion commands for 2D profiles and Box.
- `features.py`: generic Fillet, Hole, Cylinder additions/cuts and feature order.
- `placement.py`: relative anchors and parametric edge references.
- `csg.py`: primitive solids and Boolean operations for CSG compositions.
- `runner.py`: loads a trusted Python script and executes its model definition.

Plate, Bracket and both Sample Plate variants use the same `features.py`
implementation for Hole, Fillet, and sketch-based cuts/joins. No compiler
function is selected by the model's name.

## Current limits

- Supported 3D objects include `Box`, `Cylinder`, `Sphere`, plus the
  native plastic building blocks `Lip`, `SnapFit`, `Boss` and `Rest`;
  there is no `Cube` constructor or `Cylinder3D` alias.
- Supported profiles: `Rectangle2D`, `Circle2D`, `Polygon2D`, extruded
  implicitly through native SolidCraft sketches.
- Native CAD modifiers include `Hole` (blind or through-all), `.fillet()`,
  `.shell()` and positive/negative extrusion. Plastic objects compile to
  SolidCraft's native `plastic.*` features.
- `+`, `-` and `&` describe Boolean operations where supported;
  `+` on a Hole means adding the *feature* (which removes material).
- CSG translation supports intersection, union, difference and oriented cylinders.
- Anchor references are currently reliable on the supported rectangular bases;
  a joined cylindrical boss uses a numeric top-face pick for its bore.
- Arbitrary shape graphs, general topology queries, rotations, assemblies,
  solver constraints and arbitrary workplanes are not yet supported.
- SolidCraft, not SCPF, owns the geometry and native feature history.

## Sample Plate reconstruction

The saved Sample Plate has four named sketches: `Base`, `Holes`, `Boss`
and `Bore`. SCPF keeps the Python model object-oriented:

```python
holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
    count=2, spacing=self.width - 24, axis=Axis.X
).attach(plate, parent=Anchor.TOP)
plate = plate + holes

boss = Cylinder(d=24, h=14).attach(plate, parent=Anchor.TOP)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).attach(
    plate, parent=Anchor.TOP)
plate + bore
```

The compiler translates that intent to native SolidCraft sketches and
extrusions: `Holes` is one sketch with two circles, `Boss` is a joined
circle extrusion, and `Bore` is a downward cut from the current top.

## SCPF API cheatsheet

The generated results website includes a `/cheatsheet/` page.
2D profiles have an explicit suffix: `Rectangle2D`, `Circle2D` and
`Polygon2D`. 3D solids use plain names: `Box`, `Cylinder`
and `Sphere`. The direct `Cylinder(d=..., h=...)` starts at its lower face. The
`pattern()` and `orient()` helpers place repeated or oriented cylinders;
Hole patterns use native `solid.hole` features.
The old positional constructor and 3D-suffixed aliases are not supported.

## Edge and face selection

Use `Edges.VERTICAL` for automatic selection of vertical edges on supported
rectangular bodies, or supply a list of explicit 3D edge points for a
specific edge.

Face selection is a separate concept: `Faces.TOP`, `Faces.BOTTOM`, etc.
select faces for operations such as `body.shell(2, open=Faces.TOP)`.
`Anchor.TOP` remains a placement reference for `attach()`; it is not a
face-selection value. Strings such as `edges="vertical"` are no longer part
of the SCPF API.

## Relative anchors and symmetric patterns (experimental)

For a rectangular XY plate, placement can reference the plate rather than
hard-coded world coordinates:

```python
plate = Rectangle2D(100, 60).extrude(10)
holes = Cylinder(d=8, h=12).pattern(
    count=2, spacing=40, axis=Axis.Y
).attach(plate, parent=Anchor.CENTER, child=Anchor.CENTER)
plate - holes
```

`attach(target, parent=Anchor.TOP, child=Anchor.BOTTOM)` connects two
explicit anchors. `offset=(dx, dy)` is measured along the local XY axes.
Currently supported: Box or Rectangle2D extrusion bases; `Anchor.CENTER`,
`Anchor.TOP`, `Anchor.BOTTOM`; `Anchor.INNER_BOTTOM` for the inner floor
of a shelled rectangular body; and XY linear patterns of cylinders.

For X/Y placement relative to the parent bounds, use the axis-qualified
selectors `X.MIN`, `X.CENTER`, `X.MAX` and `Y.MIN`, `Y.CENTER`,
`Y.MAX`. For example:

```python
Boss(d=7, h=12, hole_d=2.5).attach(
    enclosure,
    parent=Anchor.INNER_BOTTOM,
    offset=(X.MIN + 10, Y.MAX - 10),
)
```

This means 10 mm from the minimum X edge and 10 mm from the maximum Y edge.

For `Anchor.TOP` and `Anchor.BOTTOM`, the native adapter now emits
`references` with two perpendicular straight edge picks and parametric
distances. The accompanying `base` or `position` is numeric because
SolidCraft explicitly requires numeric coordinates when using references.
The initial edge pick points are not promises of stable topology across all
changes: only a simple rectangular XY base is supported, and native
save/reopen/parameter-edit qualification is required.

`Hole(d=8, depth=Depth.THROUGH_ALL)` describes drilling intent. Use
`.attach(parent, parent=Anchor.TOP)` to choose the entry face and then add
the feature with `+`. The compiler may represent that intent as an editable
sketch plus cut extrusion. More general attachments remain tracked in issue #5.

## Sketches versus direct features

SCPF currently handles sketches **implicitly**. `Rectangle2D(...).extrude(...)`
compiles to native `sketch.create`, rectangle curves, `sketch.finish`,
and `solid.extrude`. Likewise, `Circle2D` profiles in an extruded
cut create a native sketch and subtractive extrusion. Those sketches
are preserved in SolidCraft's feature history, where they can be edited.

An attached `Hole` is compiled to an editable sketch plus cut extrusion
for the supported rectangular feature chain. A patterned Hole becomes one
sketch containing all circle profiles, not separate loose Hole features.

The user-facing Python model does **not** need to create `Sketch` objects.
The adapter creates sketches where SolidCraft requires them; they remain
editable in the native design. Full sketch constraints and arbitrary
workplanes are separate capabilities, not prerequisites for this API.
