# Experiment 011 — SolidCraft Python Forge (SCPF)

SCPF is an installable Python package, currently located in `scpf/`.
The planned CAD project will pin the library as a Git external at
`ext/scpf` and install it editable from `ext/scpf/scpf` (issue #25).
The repository rename and split have **not** happened yet.

SCPF lets you describe CAD models with Python objects. The Python layer translates
those operations into **native SolidCraft commands**; SolidCraft performs the
actual geometry and retains editable CAD features. No separate BRep engine is used.

## Windows quick start

Open PowerShell in the **repository root**. Python 3.12 and the
official SolidCraft 0.30.1 CLI are used in CI.

```powershell
# Install the library into the active Python/Conda environment
# (the project repository will later install from ext/scpf/scpf).
python -m pip install -e .\scpf

# Legacy development alternative, without installing:
# $env:PYTHONPATH = "scpf"

# Run tests
python -m unittest discover -s scpf/tests -v

# Generate the exact native SolidCraft commands from a Python model
python -m scpf examples/sample-plate/scpf/model.py --out output/sample-plate.json

# Inspect those commands in VS Code
code output/sample-plate.json

# Build a native, editable SolidCraft design and STEP file
solidcraft-cli run output/sample-plate.json --param-check strict --results --save output/sample-plate.sc --out output/sample-plate.step

# Inspect the saved design, including generated features
solidcraft-cli eval output/sample-plate.sc --json-out output/sample-plate-measurements.json
```

Alternatively, with SolidCraft open in a **new empty design** and external
Assistant control enabled, run:

```powershell
python -m scpf examples/sample-plate/scpf/model.py --connect
```

The `--connect` command changes the open design; it does not write the
generated JSON. Use `--out` first to inspect the exact sequence.

## Reusable components (assembly experiment)

A model class can be instantiated more than once. SCPF compiles identical
instances into one native SolidCraft component definition with separate
occurrences; `attach()` creates a rigid joint between matching faces.

The first working example is [TwoBlocks](examples/components/scpf/model.py).
It uses explicit Python `return` statements in `build()`. The current
assembly boundary is deliberately limited to axis-aligned rectangular
components and face-centre matching with no offsets or rotations. Native
SolidCraft qualification verifies the saved component occurrences and joint.

## Examples

- [Sample Plate — original history](examples/sample-plate/scpf/model.py):
  four named sketches (`Base`, `Holes`, `Boss`, `Bore`) and matching
  sketch-based cut/extrusion operations.
- [Plate](examples/plate/scpf/model.py): rectangular mounting plate.
- [Bracket](examples/bracket/scpf/model.py): polygon-based angle bracket.
- [CSG Cube](examples/csg-cube/scpf/model.py): primitive Boolean operations.
- [HUB75 panel pair](examples/hub75-panel/scpf/model.py): first measured
  159.70 × 319.71 mm portrait panel component with mounting holes and two
  native occurrences at a 160 mm pitch. This is an envelope reference, not yet
  the full electronic/structural model. See [limitations](examples/hub75-panel/README.md).
- [Anchored Holes](examples/anchored-holes/scpf/model.py): repeated
  Hole intent attached to the plate and compiled as one editable sketch cut.
- [Plastic Enclosure](examples/plastic-enclosure/scpf/model.py): native
  Shell, Lip, Snap Fit, Boss and Rest plastic features.

A `Hole` describes drilling intent. Attach it to the face where drilling
starts, then add it to the body with `+`. For the Sample Plate, the compiler
creates editable `Holes` and `Bore` sketches plus cut extrusions; the Python
model does not create explicit Sketch objects.

See the [SCPF guide](scpf/README.md) for models, parameters, placement,
the live GUI connection and limitations.

## Result pages and native evidence

The [results-site generator](scripts/ci/build-results.py) publishes the
Python model, exact native SolidCraft command JSON, and a command-by-command
timeline. The exact command and parameters are shown directly below every
step. Native CAD snapshots are verified against the source commit
before they are marked verified.

The formerly experimental Rust scripting layer (SCRF) has been retired.
Other CAD implementations in `examples/` are kept as **comparison
references**, not as SCPF runtime dependencies.
