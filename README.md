# Experiment 011 — SolidCraft Python Forge (SCPF)

SCPF lets you describe CAD models with Python objects. The Python layer translates
those operations into **native SolidCraft commands**; SolidCraft performs the
actual geometry and retains editable CAD features. No separate BRep engine is used.

## Windows quick start

Open PowerShell in the **repository root**. Python 3.12 and the
official SolidCraft 0.30.1 CLI are used in CI.

```powershell
# Install the Python scripting package
python -m pip install -e ./scpf

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

## Examples

- [Sample Plate — original history](examples/sample-plate/scpf/model.py):
  four named sketches (`Base`, `Holes`, `Boss`, `Bore`) and matching
  sketch-based cut/extrusion operations.
- [Plate](examples/plate/scpf/model.py): rectangular mounting plate.
- [Bracket](examples/bracket/scpf/model.py): polygon-based angle bracket.
- [CSG Cube](examples/csg-cube/scpf/model.py): primitive Boolean operations.
- [Anchored Holes](examples/anchored-holes/scpf/model.py): repeated
  native holes positioned relative to the plate.

A `Hole` describes drilling intent. Attach it to the face where drilling
starts, then add it to the body with `+`. For the Sample Plate, the compiler
creates editable `Holes` and `Bore` sketches plus cut extrusions; the Python
model does not create explicit Sketch objects.

See the [SCPF guide](scpf/README.md) for models, parameters, placement,
the live GUI connection and limitations.

## Result pages and native evidence

The [results-site generator](scripts/ci/build-results.py) publishes the
Python model, exact native SolidCraft command JSON, and a command-by-command
timeline. Expand **Show exact command and parameters** to inspect the actual
JSON for a step. Native CAD snapshots are verified against the source commit
before they are marked verified.

The formerly experimental Rust scripting layer (SCRF) has been retired.
Other CAD implementations in `examples/` are kept as **comparison
references**, not as SCPF runtime dependencies.
