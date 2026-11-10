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

The saved source of Sample Plate has sketch-based mounting holes and bore;
our Python model uses native Hole features, so feature counts and types
intentionally differ. Evaluate geometry and parameter changes separately.
