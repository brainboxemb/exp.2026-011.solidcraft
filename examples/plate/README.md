# Plate — native SolidCraft Python model

The SCPF [Python model](scpf/model.py) produces a 100 × 60 × 10 mm plate,
with R2 fillets on the vertical outside edges and four Ø8 through holes
at (±35, ±15) mm. The expected volume is about 57,955 mm³.

The [reviewed SolidCraft commands](scpf/reference.json) are retained as
a regression fixture for the Python compiler. Generate a fresh command
plan with:

```powershell
python -m scpf examples/plate/scpf/model.py --out output/plate.json
code output/plate.json
```

Additional CadQuery, vcad, µcad and PythonSCAD variants are independent
comparison references, not scripting runtimes for this project.
