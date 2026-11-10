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

## Run

From the repository root, with Python >=3.10 (no third-party runtime dependencies):

```powershell
$env:PYTHONPATH = "scpf"
python -m unittest discover -s scpf/tests -v
python -m scpf examples/plate/scpf/model.py --out output/examples/plate/scpf/solidcraft.json
python -m scpf examples/csg-cube/scpf/model.py --out output/examples/csg-cube/scpf/solidcraft.json
```

On Windows, use the project-local Python executable if preferred.
Alternatively, install the package with `python -m pip install -e ./scpf`.

The Rust predecessor is **SCRF** (SolidCraft Rust Forge); SCPF is the Python successor. The Rust implementation and its fixtures now live under `scrf/` and `examples/{plate,csg-cube}/scrf/`. The old directory layout is preserved only in Git history.

The tests compare each generated command document with the
reviewed SCRF reference JSON. CI keeps the two SCPF JSON
documents as artifacts; the integrated build workflow also includes them
in the orphan `bld` branch after all build checks pass. The native
qualification pipeline keeps verified SolidCraft outputs in `vrf`.

The previously agreed `generated-examples` branch remains gated by
verification of the comparison implementations.

## Open generated JSON in the SolidCraft desktop GUI

SCPF generates a **command script**, not an already saved SolidCraft design.
The GUI's File > Open reads design files (including self-contained design
JSON), but does not treat a command script as a saved design. Execute the
commands with the CLI first, then open the resulting native `.sc`:

```powershell
.\scripts\open-solidcraft-json.ps1 -Script "output/examples/plate/scpf/solidcraft.json"
```

This helper validates parameters strictly, saves a native `.sc` alongside
the command JSON and launches SolidCraft. It uses `solidcraft-cli` and
`solidcraft` from PATH or the default Windows installation directory. If
necessary pass `-Cli` and `-Gui` with explicit executable paths, or use
`-NoOpen` for headless execution.

Equivalent manual command:

```powershell
solidcraft-cli run examples/plate/scrf/solidcraft.json --param-check strict --save plate.sc
solidcraft plate.sc
```

The original bracket reference contains `parameters.change` without
preceding `parameters.add`. It therefore expects an existing SolidCraft
document with those parameters; use the generated standalone SCPF bracket
command plan instead. Its corrected fillet and cut direction still require
native qualification.

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
