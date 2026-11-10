# SCPF — SolidCraft Python Forge (proof of concept)

SCPF describes CAD models in ordinary Python and compiles them to
**native SolidCraft command JSON**. It is not a second geometry engine,
not a SolidCraft MCP implementation, and does not replace SolidCraft's
own MCP/RPC control interface.

The objective is a compact model language with useful CSG and CAD features:
readability first, fewer nested operations than OpenSCAD, while preserving
native SolidCraft feature history when possible.

## Two models

`examples/csg-cube/scpf/model.py`:

```python
def CsgCube(size=50.0):
    body = Sphere(size / 1.5) & Cube(size)
    holes = Cylinder(size, size / 1.5).orient(X, Y, Z)
    return body - holes

CsgCube()
```

`examples/plate/scpf/model.py`:

```python
def Plate(length=100.0, width=60.0, thickness=10.0):
    body = Box(length, width, thickness).fillet(2.0, edges="vertical")
    holes = Cylinder(thickness, 8.0).pattern(x=70.0, y=30.0)
    return body - holes

Plate()
```

The four hole centres are (±35, ±15) mm; the pattern values specify
**centre-to-centre spacing**. The top face's four holes are compiled as a
native SolidCraft sketch plus a subtractive extrusion, not a mesh.

No `import`, `self`, `main()`, `show()`, `Result`, `?`,
`#[cad]` or `#[parameter]` is required in model files.

## Parameters

The runner reads the final model function's Python signature using
`inspect.signature`. Numerical arguments become named CAD parameters,
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

The tests compare each generated command document with the
reviewed SolidCraftForge reference JSON. CI keeps the two SCPF JSON
documents as artifacts; the integrated build workflow also includes them
in the orphan `bld` branch after all build checks pass. The native
qualification pipeline keeps verified SolidCraft outputs in `vrf`.

The previously agreed `generated-examples` branch remains gated by
verification of the comparison implementations.

## Current limits

- Supported primitives: box (feature model), cube, sphere, cylinder.
- CSG: intersection, union, difference, and oriented cylinder cutters.
- Feature model: box, vertical-edge fillet, rectangular pattern of four
  through-cylinder cutters. These are exact native SolidCraft features
  after running the resulting commands.
- This is an explicit, narrow translation layer: arbitrary Python code
  can execute, but not every shape composition can be compiled into
  SolidCraft commands yet.
- Positioning, general face/edge selectors, arbitrary patterns,
  more dimensional arithmetic and model reuse are future work.
- SolidCraft, not SCPF, remains responsible for topology, solving and geometry.
