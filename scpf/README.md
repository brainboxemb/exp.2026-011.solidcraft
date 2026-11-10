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
        holes = Cylinder(self.thickness, 8).pattern(x=70, y=30)
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
    body = Sphere(size / 1.5) & Cube(size)
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

The Rust predecessor is **SCRF** (SolidCraft Rust Forge), stored under
`scrf/` and `examples/{plate,csg-cube}/scrf/`.

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
