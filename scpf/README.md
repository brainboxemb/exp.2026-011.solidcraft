# SCPF — SolidCraft Python Forge (proof of concept)

SCPF describes CAD models in ordinary Python and compiles them to
**native SolidCraft command JSON**. It is not a second geometry engine,
not a SolidCraft MCP implementation, and does not replace SolidCraft's
own MCP/RPC control interface.

The objective is a compact model language with useful CSG and CAD features:
readability first, fewer nested operations than OpenSCAD, while preserving
native SolidCraft feature history when possible.

See [How SCPF works](docs/architecture.md) for a beginner-friendly explanation
of which work belongs in Python and which belongs in SolidCraft, including
the lessons from the HUB75 rotation bug.

## External package installation

SCPF is a standalone Python package in `scpf/pyproject.toml`, maintained by
[lib.py.solidcraft](https://github.com/brainboxemb/lib.py.solidcraft).
Install editable in your active environment from this library checkout:

```powershell
python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
```

The independent [SolidCraft CAD project](https://github.com/brainboxemb/2026-011-02.cad.solidcraft)
consumes a pinned Git SHA using **vcs2l**, not Git submodules. It places the library
at `ext/scpf` and installs from `ext/scpf/scpf` through `bootstrap.ps1`.
Users of the CAD project do **not** set `PYTHONPATH`; they run the root bootstrap.

Library issue [#25](https://github.com/brainboxemb/lib.py.solidcraft/issues/25)
tracks the separation of CAD assets from reusable API implementation.

## Full library documentation

The [published API Guide](https://brainboxemb.github.io/lib.py.solidcraft/guide/)
explains topics step by step: first model, geometry, transformations, features,
assemblies and verification. This README retains developer-oriented reference
notes; the cheatsheet is only a quick syntax lookup.

**Important:** the current occurrence `rotate()` sets one absolute axis-angle
pose. Calling it twice does not combine two rotations. `rotate(Z, 180)`
is not yet a supported shorthand; use `rotate(axis=(0, 0, 1), degrees=180)`.

## Supported SolidCraft version

The native command adapter and verification tests target **SolidCraft 0.30.1**.
The library's `scpf.version.check_cli_version()` reads
`solidcraft-cli --version`, **rejects older versions**, and emits a warning
for newer or unverified versions. It is run automatically by the live SCPF
CLI before sending model commands when a local CLI is available.
If the local CLI is not installed, a warning explains that the separate
GUI version cannot be checked; `--out` works without SolidCraft.
The installed CLI may differ from the GUI process, so it is only a proxy,
not proof of which GUI version is running.

For strict CI/headless checks:

```python
from scpf.version import check_cli_version
check_cli_version(require_cli=True)
```

### How placement works in SolidCraft 0.30.1

SCPF does **not** calculate 3D transformation matrices. It tells SolidCraft
where each occurrence belongs and lets SolidCraft apply the move and rotation.

A component definition is the **part itself**. An occurrence is **one placed
copy** of that part. For a reusable component, SCPF compiles these steps:

1. Create the component definition once, including its editable features.
2. Create the additional occurrences **at the origin**. Each copy initially
   has no translation or rotation. This prevents copied positions or
   orientations from accumulating.
3. Move each occurrence once, using native SolidCraft
   `occurrence.move` with `translate` and, if needed, `axis` and `angle`.

For example:

```python
from scpf import component, Box

class Panel:
    def build(self):
        return Box(160, 320, 14.5)

PanelComponent = component(Panel)

class Pair:
    def build(self):
        left = PanelComponent().rotate(axis=(1, 0, 0), degrees=90)
        right = left.copy().move(x=160)
        return left + right

Pair()
```

Both occurrences are built from **one** editable component. SCPF first
creates the second occurrence, then sends each occurrence's translation and
rotation to SolidCraft. It does **not** calculate a matrix or apply the same
rotation repeatedly.

The native commands for the first occurrence resemble:

```json
{
  "command": "occurrence.move",
  "params": {
    "occurrence": "Panel:1",
    "translate": [0, 0, 0],
    "axis": [1, 0, 0],
    "angle": "90 deg",
    "move_grounded": true
  }
}
```

**Why this matters:** SolidCraft 0.30.1 accepts `translate`, `axis`,
`angle` and `origin`, but does **not** support the newer
`to: {position, axis, angle}` syntax. An older command runner could
silently ignore that unsupported `to` field, leaving panels flat while
a JSON syntax test passed. Using native parameters and checking the
**saved SolidCraft transforms** avoids that false success.

`rotate()` currently **sets** one requested axis-angle orientation on
the Python occurrence. Calling `rotate()` twice **replaces** the first
setting; it does not compose two rotations. When an assembly needs a more
complicated final orientation, express it as one axis-angle and let
SolidCraft perform that rotation.


## Model objects

The preferred SCPF style is a plain Python class. Numeric class fields are
CAD parameters, and `build()` constructs the model. An explicit `return` makes the resulting Shape clear to ordinary Python
readers; there is no need for `show()` or `main()`.

```python
class Plate:
    length = 100.0
    width = 60.0
    thickness = 10.0

    def build(self):
        body = Box(self.length, self.width, self.thickness)
        body = body.fillet(2, edges=Edges.VERTICAL)
        return body

Plate()
```

SCPF promotes those numeric class fields to SolidCraft parameters and also
allows overrides such as `Plate(width=80.0)` without requiring a handwritten
`__init__`. Existing `@dataclass` models remain supported, including
`@dataclass(frozen=True)` and `__post_init__` validation. An implicit final Shape expression remains supported for older scripts,
but examples now prefer ordinary Python `return` syntax.

The real CAD examples, model specifications and native screenshots are now
maintained in the [CAD model catalog](https://github.com/brainboxemb/2026-011-02.cad.solidcraft/tree/main/models):
Plate, CSG Cube, Bracket, Sample Plate, Plastic Enclosure, Pi enclosure, Corner
Bracket and HUB75 Panel. The library retains only lightweight API fixtures.

Older function models with an implicit final Shape expression remain
supported. Ordinary helpers still use standard Python semantics.

## Imported reusable model classes

When two project scripts need the same component, keep its class in **one**
Python module and explicitly wrap the imported class:

```python
from scpf import component
from models.hub75_panel import Hub75Panel as PanelDefinition

Hub75Panel = component(PanelDefinition)
```

Then `Hub75Panel()` produces a reusable native component instance, just
like a model class declared in the same script. No source-copying or
private runner hooks are required. The import module must be available in
Python's usual import path.

## Named subassemblies in the SolidCraft browser

A set of reused component occurrences can be placed under one **real
nested SolidCraft component** using `.group("HUB75Panels")`:

```python
first = Hub75Panel()
panels = (first + first.copy().move(x=160)).group("HUB75Panels")
return panels + WoodenFrame()
```

SolidCraft receives `component.create(name="HUB75Panels", activate=False)`,
then creates the panel's shared definition **with parent HUB75Panels**.
The browser shows one expandable group rather than five top-level panels.
The member occurrences still share one editable native definition.

Current limit: one shared component definition must have all its
occurrences under the same parent group (or all at the root); placing the
same definition under multiple different groups is not supported yet.
Grouping itself does not apply an extra transform or rigid joint.

## Native component occurrence rotation

A reusable model definition can be placed more than once without duplicating
its editable SolidCraft feature history. Use `copy()`, `move()`, and a
single absolute axis-angle `rotate()` for each placement:

```python
first = Hub75Panel()
second = first.copy().move(x=160).rotate(axis=(0, 0, 1), degrees=180)
return first + second
```

SCPF sends the native `occurrence.move` parameters
`translate`, `axis` and `angle`. It does not implement 3D rotation
or matrix arithmetic. The native operation rotates the occurrence, not
the underlying component definition.

The current API supports one axis-angle orientation per occurrence, not
chained rotations, rotation of arbitrary Shapes, or associative sketch
constraints.

For real geometry and native CI results see the
[CAD project](https://github.com/brainboxemb/2026-011-02.cad.solidcraft).

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

Plain model classes use naming to make parameter intent explicit:

```python
class Display:
    PANEL_COUNT = 5          # fixed constant: never a SolidCraft parameter
    _panel_pitch = 160.0     # Forge/build-time input: Python only
    opening_width = 844.0    # model parameter: must remain native/editable
```

A public lower-case numeric field is a **model parameter**. SCPF expects it
to survive as a native SolidCraft dependency. If compilation consumes it only
as a concrete Python value, for example through `pv()`, SCPF emits a
`ModelParameterWarning`. Rename an intentionally build-time input with a
leading underscore instead of silently publishing a parameter that cannot
update the native model.

Upper-case numeric class attributes are constants. They stay available to
`build()` but are not constructor/model parameters. Underscore-prefixed
numeric fields remain private constructor/build inputs. Their own numeric
defaults are deliberately concrete and are never emitted as native SolidCraft
parameters. When a parent assembly explicitly passes a `Parameter` or
expression into such a private input, that parent dependency remains symbolic.

The final model call may override public model parameters and Forge/build
inputs by name or position:

```python
Plate(width=80.0)
Display(_panel_pitch=161.0)
```

A reusable component source file can itself be run directly when it defines
exactly one public class with `build()`:

```python
# components/corner_bracket.py
class CornerBracket:
    ...
    def build(self):
        ...
```

Run that file directly:

```powershell
python -m scpf components/corner_bracket.py --connect
```

No trailing `CornerBracket()`, launcher file, wrapper class or alternate
geometry path is required. If a file defines multiple public model classes,
SCPF refuses to guess; finish the script with an explicit model call instead.

An imported class can still be selected explicitly when a composition script
needs one particular model.

Reusable component parameters are implicit. A public lower-case numeric
default becomes an editable component-local parameter automatically. Forge
namespaces local component parameters when needed to avoid collisions.

Passing an existing parent `Parameter` or expression into a component input
reuses that dependency directly:

```python
Bracket(
    bracket_width=self.bracket_width,
    inside_corner_radius=self.corner_radius,
)
```

Both child inputs then depend on the parent's native model parameters rather
than creating duplicate child parameters. No separate publication or alias
declaration is required.

Dataclass models continue to use their normal constructor signature.

SCPF preserves symbolic expressions such as `size / 1.5` in emitted JSON.
For the supported box, parameters `length`, `width` and `thickness`
become native SolidCraft parameters and remain editable in native history.
This is **not** automatic tracking of arbitrary Python calculations.
The first version supports simple parameter arithmetic and predefined
operations only.

Plain numbers mean millimetres. SCPF scripts are real Python: only execute
trusted model files.

## Running from a model subfolder

The normal live GUI workflow is `python -m scpf model.py --connect`.
A project model can import shared classes via `from models.components... import ...`
even when you run the command **inside** `models/<slug>/scpf/`.
SCPF temporarily resolves the project root based on the `models/`
directory and restores Python's import path after compiling. No manual
`PYTHONPATH` is needed.

Open SolidCraft, create a fresh empty design, enable
**Preferences → Assistant → Let AI agents connect**, then:

```powershell
# From models/hub75-wood-frame/scpf/
python -m scpf model.py --connect
```

This sends native commands to the **active** SolidCraft design, but does not
create or save a document. `--out` is only for JSON generation.

## Run and inspect a CAD model

Use the [CAD project repository](https://github.com/brainboxemb/2026-011-02.cad.solidcraft)
for real model runs, not this library repository:

```powershell
# In 2026-011-02.cad.solidcraft
.\bootstrap.ps1
python -m scpf models/bracket/scpf/model.py --out output/bracket.json
code output/bracket.json
solidcraft-cli run output/bracket.json --param-check strict --save output/bracket.sc
```

Alternatively, with the SolidCraft GUI open in a new empty document and
external Assistant control enabled, run:

```powershell
python -m scpf models/bracket/scpf/model.py --connect
```

`--out` generates native command JSON without modifying an open document.
`--connect` applies commands to the GUI. Open `output/bracket.sc` to inspect
the editable native history produced by the CLI.

## Results website

The [CAD project's results website](https://brainboxemb.github.io/2026-011-02.cad.solidcraft/)
publishes model source, generated command plans, and native SolidCraft renders
with source-matched verification. The CAD project, not the Python library,
owns `scripts/ci/build-results.py`, `site/` and its publication workflows.

The [library website](https://brainboxemb.github.io/lib.py.solidcraft/)
publishes a cheatsheet and a small set of source-matched command examples
(SimpleBox, AnchoredHoles, TwoBlocks). The full model gallery, render evidence
and native qualification remain in the CAD project. Old experiment pages
are retained in Git history, not copied to the active library site.

## Code organization

The compiler is divided by **responsibility**, not by example model:

- `core.py`: user-facing Python shapes, parameters, anchors, operations.
- `compiler.py`: small entry point and parameter collection.
- `sketches.py`: native base-body lowering for `Box` and explicit `Sketch` extrusions.
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
- Supported profiles: `Rectangle2D`, `Circle2D`, `Polygon2D`; 2D geometry is
  authored inside an explicit `with Sketch(...)` scope and extruded from that sketch.
- Native CAD modifiers include `Hole` (blind or through-all), `.fillet()`,
  `.shell()` and positive/negative extrusion. Plastic objects compile to
  SolidCraft's native `plastic.*` features.
- `+`, `-` and `&` describe Boolean operations where supported;
  `+` on a Hole means adding the *feature* (which removes material).
- CSG translation supports intersection, union and difference; general primitive rotation/orientation remains a separate API gap.
- Anchor references are currently reliable on the supported rectangular bases;
  a joined cylindrical boss uses a numeric top-face pick for its bore.
- Basic reusable component definitions, occurrences and copy placement are
  implemented and native-qualified for the HUB75 pair. General rotations,
  arbitrary assembly constraints and generic topology queries remain limited.
- SolidCraft, not SCPF, owns the geometry and native feature history.

## Sample Plate reconstruction

The saved Sample Plate has four named sketches: `Base`, `Holes`, `Boss`
and `Bore`. SCPF keeps the Python model object-oriented:

```python
holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
    count=2, spacing=self.width - 24, axis=Axis.X
).on(plate, face=Faces.TOP)
plate = plate + holes

boss = Cylinder(d=24, h=14).on(plate, face=Faces.TOP)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).on(
    plate, face=Faces.TOP)
plate + bore
```

The compiler translates that intent to native SolidCraft sketches and
extrusions: `Holes` is one sketch with two circles, `Boss` is a joined
circle extrusion, and `Bore` is a downward cut from the current top.

## SCPF API cheatsheet

The generated results website includes a `/cheatsheet/` page.
2D profiles have an explicit suffix: `Rectangle2D`, `Circle2D` and
`Polygon2D`. 3D solids use plain names: `Box`, `Cylinder`
and `Sphere`. The direct `Cylinder(d=..., h=..., axis=Axis.Z)` starts at its base point; set `axis=Axis.X` or `Axis.Y` for the other native principal axes.
Use `shape.at(x, y, z)` for absolute placement. For direct CSG geometry,
`shape.at(target)` places CENTER on the target CENTER; the explicit form is
`shape.at(target, anchor=Anchor.CENTER, child=Anchor.CENTER)`.
`pattern()` places repeated cylinders; Hole patterns use native
`solid.hole` features.
The old positional constructor and 3D-suffixed aliases are not supported.

## Edge and face selection

Cardinal directions use one shared BOSL2-style vocabulary:
`TOP`, `BOTTOM`, `LEFT`, `RIGHT`, `FRONT` and `BACK`.
Add two directions to identify one rectangular-solid edge, for example
`BOTTOM + LEFT` or `TOP + RIGHT`.

A native Box can also be positioned by one of those anchors:

```python
board = Box(width, depth, height).at(
    x,
    y,
    z,
    anchor=FRONT + BOTTOM,
)
board = board.fillet(
    radius,
    edges=[BOTTOM + LEFT, BOTTOM + RIGHT],
)
```

This remains a native `solid.box`; Forge does not synthesize a Sketch.
`Edges.VERTICAL` remains available for selecting all vertical edges on
supported rectangular bodies, and explicit 3D edge points remain supported.

Face selection is also used for simple within-component placement:
`feature.on(body, face=Faces.TOP)`. The same `Faces` values select geometry
for operations such as `body.shell(2, open=Faces.TOP)`.

`Anchor` is reserved for explicit relationships between reusable component
occurrences at assembly level. It is not the ordinary way to choose the top or
bottom surface for a Hole, Boss or Cylinder. Strings such as
`edges="vertical"` are no longer part of the SCPF API.

## Relative anchors and symmetric patterns (experimental)

For a rectangular XY plate, placement can reference the plate rather than
hard-coded world coordinates:

```python
with Sketch(plane="XY") as sketch:
    Rectangle2D(100, 60)
plate = sketch.extrude(10)
holes = Cylinder(d=8, h=12).pattern(
    count=2, spacing=40, axis=Axis.Y
).attach(plate, parent=Anchor.CENTER, child=Anchor.CENTER)
plate - holes
```

`attach(target, parent=Anchor.TOP, child=Anchor.BOTTOM)` connects two
explicit anchors. `offset=(dx, dy)` is measured along the local XY axes.
Currently supported: Box or explicit rectangular Sketch extrusion bases; `Anchor.CENTER`,
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
`.on(parent, face=Faces.TOP)` to choose the entry face and then add the
feature with `+`. The compiler may represent that intent as an editable
sketch plus cut extrusion.

The older shape-level `attach(..., Anchor...)` form remains temporarily for
advanced legacy placements such as `CENTER` and `INNER_BOTTOM`; new simple
surface placement should use `on(..., face=Faces...)`.


For reusable **components in an assembly**, `ModelInstance.attach()` uses
`Anchor` as an explicit attachment reference. Face anchors such as
`Anchor.RIGHT` and `Anchor.LEFT` are native associative SolidCraft joint
origins. Corner anchors are also available for rectangular components:

```python
marker = Marker().attach(
    base,
    parent=Anchor.FRONT_TOP_RIGHT,
    child=Anchor.BACK_TOP_RIGHT,
)
```

The eight corner anchors combine `FRONT/BACK`, `TOP/BOTTOM` and
`LEFT/RIGHT`. Forge lowers them to SolidCraft `edge + corner` origins.
SolidCraft keeps the referenced edge, face and corner by topology name, so the
attachment follows dimension changes in a saved design. No public `Joint`
object is exposed; native joints are an implementation detail of `attach()`.


Non-rectangular components can define their own named local attachment frames:

```python
class CornerBracket:
    def anchors(self):
        return {
            "mount": AnchorFrame(
                origin=(0, 0, 0),
                z=(0, 0, 1),
                x=(1, 0, 0),
            ),
        }
```

Use the name in `attach()`, for example `child="mount"`. The frame belongs
to the reusable component definition. Forge creates the native SolidCraft
joint origin before occurrence placement, so later `move()` or `rotate()`
operations carry that anchor with the occurrence. `AnchorFrame` is a fixed
component-local datum; it is not a public Joint object and it does not itself
track changing component geometry.

## Sketches versus direct features

SCPF does **not** synthesize sketches for 3D primitives. `Box(...)` lowers
directly to SolidCraft's native `solid.box` command; the same principle applies
to other native 3D primitives.

2D geometry is intentionally explicit. Create profiles inside a `Sketch`
scope, leave the scope, and extrude the sketch:

```python
with Sketch(plane="XY") as sketch:
    Rectangle2D(100, 60)

plate = sketch.extrude(10)
```

This produces native `sketch.create`, profile geometry, `sketch.finish` and
`solid.extrude` history. Direct `Rectangle2D(...).extrude(...)`,
`Circle2D(...).extrude(...)` and `Polygon2D(...).extrude(...)` are not part
of the Forge API.

An attached `Hole` may still lower to editable sketch/cut history where that
is the selected SolidCraft feature strategy; that is feature lowering, not an
implicit user sketch.

## Rear-plane sketches on tapered solids

A `Box(...).taper(...)` can accept a named `Sketch` with an explicit rear XY origin and a negative finite-depth pocket; it retains the front mask. Complex rounded openings and multiple physical materials require additional native geometry.

## Native rounded rectangles in explicit sketches

`RoundedRectangle2D(width, depth, radius)` creates one **true native rounded-rectangle sketch profile** in a `Sketch` scope. Its four corners are circular arcs, generated by SolidCraft's `sketch.rectangle.rounded` command, not a collection of intersected solids or polygon facets. The radius must be positive and smaller than half the shorter edge.

```python
with Sketch(name="Rear bay", on=panel, parent=Anchor.TOP) as sketch:
    sketch.add(RoundedRectangle2D(130, 60, 5), offset=(-65, -150))
panel = panel - sketch.extrude(12.5, direction=Direction.NEGATIVE)
```

Like all 2D profiles, `RoundedRectangle2D` is authored inside an explicit `Sketch`; direct profile `.extrude()` syntax is not part of the API.
