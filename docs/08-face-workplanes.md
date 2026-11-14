# Face references and workplanes — Python SCPF

SCPF allows relative placement without exposing native command names to a
Python model. Currently supported anchor selectors are intentionally narrow:
`Anchor.TOP`, `Anchor.BOTTOM`, and `Anchor.CENTER`.

## Working syntax

```python
with Sketch(name="Base", plane="XY") as sketch:
    Rectangle2D(80, 50)
plate = sketch.extrude(8)
boss = Cylinder(d=24, h=14).attach(
    plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).attach(
    plate, parent=Anchor.TOP)
plate + bore
```

The attached `Cylinder` remains a native 3D primitive and lowers directly
to SolidCraft `solid.cylinder` with a join operation; Forge does not create
a sketch for it. A simple face-attached `Hole` currently lowers to an
editable circle sketch plus cut extrusion. Explicitly positioned directional
or countersunk holes use native `solid.hole`. When the target includes the
supported centered joined cylinder, the bore's top face is at
`thickness + 14 mm`.

## Limits

Native `solid.cylinder` can retain straight-edge references when an attached
cylinder is placed on a supported rectangular face. A simple attached Hole
still uses the sketch/cut path described above. On a circular boss, the
current implementation uses a numeric top-face position for that hole,
**not a stable topological face-reference constraint**. Its initial geometry
may therefore be correct without the hole position being fully associative
under changes to the boss dimensions.

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
