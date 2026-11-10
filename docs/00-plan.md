# Experiment 011 — Python SCPF plan

## Objective

Write readable, reusable Python CAD objects that translate to native SolidCraft
commands and editable native history. Do not implement a second geometry engine.

## Model flow

1. A Python dataclass defines dimensions and a `build()` model.
2. SCPF resolves symbolic parameters and supported feature intent.
3. The adapter generates SolidCraft JSON commands.
4. SolidCraft executes the commands and owns the resulting BRep and feature history.
5. CI compares reviewed fixtures and verifies native geometry, saved `.sc` history,
   parameter edits, and optional screenshots.

## Scope

- 2D `Rectangle2D`, `Circle2D`, `Polygon2D` and extrusions.
- 3D `Box`, `Cube`, `Sphere`, `Cylinder`.
- CAD features including `Hole`, `fillet`, anchor placement and patterns.
- Implicit sketches may be created by the adapter, but users are not required
  to construct them in Python.

## Examples

`examples/plate/scpf/`, `examples/csg-cube/scpf/`,
`examples/bracket/scpf/`, `examples/sample-plate/scpf/` and
`examples/anchored-holes/scpf/`.

## Comparison references

CadQuery, PythonSCAD, µcad and vcad examples remain for syntax and
representation comparison only; none is a SCPF runtime dependency.

## Validation

From the repository root in PowerShell:

```powershell
python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
python -m scpf examples/sample-plate/scpf/model.py --out output/sample-plate.json
solidcraft-cli run output/sample-plate.json --param-check strict --save output/sample-plate.sc --out output/sample-plate.step
```
