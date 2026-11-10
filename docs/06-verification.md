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

The default Sample Plate now reproduces the original four sketches
(`Base`, `Holes`, `Boss`, `Bore`) and their feature operations.
The alternative `examples/sample-plate/scpf/native-holes.py` uses three
SolidCraft native Hole features and only two sketches. CI qualifies both
versions independently. A native Hole intentionally does not create a sketch.
