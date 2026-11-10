# Verification — Python SCPF and SolidCraft

Run the Python regression suite from the repository root:

```powershell
python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
```

Generate the native command plan:

```powershell
python -m scpf examples/sample-plate/scpf/model.py --out output/sample-plate.json
code output/sample-plate.json
```

Execute and evaluate using the official SolidCraft CLI:

```powershell
solidcraft-cli run output/sample-plate.json --param-check strict --results --save output/sample-plate.sc --out output/sample-plate.step
solidcraft-cli eval output/sample-plate.sc --json-out output/sample-plate-measurements.json
```

GitHub Actions has a fast Python-model check and a separate native
SolidCraft qualification. Compare exact command types, native geometry,
and saved feature history; do not claim that a script matches a source
document's history unless that comparison actually passes.

The Sample Plate qualification requires the native feature history to contain
four sketches: `Base`, `Holes`, `Boss`, and `Bore`. The object-level
Hole/Cylinder Python code is therefore verified not only for final geometry,
but also for the generated sketch/cut/join history.
