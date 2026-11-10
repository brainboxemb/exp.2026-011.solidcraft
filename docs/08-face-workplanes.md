# Face references and workplanes — Python SCPF

SCPF allows relative placement without exposing native command names to a
Python model. Currently supported anchor selectors are intentionally narrow:
`Anchor.TOP`, `Anchor.BOTTOM`, and `Anchor.CENTER`.

## Working syntax

```python
plate = Rectangle2D(80, 50).extrude(8)
boss = Cylinder(d=24, h=14).attach(
    plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).attach(
    plate, parent=Anchor.TOP)
plate + bore
```

The adapter compiles `boss` into a circle sketch and join extrusion.
`Hole` compiles into a native SolidCraft `solid.hole` feature. When the
target includes the supported centered joined boss, the bore's top face
is at `thickness + 14 mm`.

## Limits

The native Hole API accepts numerical picking coordinates. On a plain
rectangular face, SCPF can also attach two parametric edge references.
For a circular boss, the current implementation supplies a numeric
top-face pick, **not a stable topological face-reference constraint**.
Its initial geometry may be correct without its hole position being
fully associative under changes to the boss dimensions.

This is not a generic `faces(">Z")` selector. The supported path is a
rectangular base and at most one centered joined cylindrical boss.
Native execution, save/reopen, parameter edits and a GUI inspection are
required for full qualification.

## Windows commands

From the repository root:

```powershell
python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
python -m scpf examples/sample-plate/scpf/model.py --out output/sample-plate.json
code output/sample-plate.json
solidcraft-cli run output/sample-plate.json --param-check strict --results --save output/sample-plate.sc --out output/sample-plate.step
solidcraft-cli eval output/sample-plate.sc --json-out output/sample-plate-measurements.json
```
