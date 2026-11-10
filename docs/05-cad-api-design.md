# Python CAD API design

SCPF exposes CAD objects, not JSON commands, transports, or an independent
geometry engine.

## User-facing model

```python
holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
    count=2, spacing=self.width - 24, axis=Axis.X
).attach(plate, parent=Anchor.TOP)
plate = plate + holes

boss = Cylinder(d=24, h=14).attach(
    plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).attach(
    plate, parent=Anchor.TOP)
plate + bore
```

## Semantics

- `attach()` is the single relative-placement mechanism.
- For a Hole, `parent=Anchor.TOP` means drilling starts at the current top
  surface and proceeds inward.
- `+` adds the described CAD feature to the model; for Hole intent the
  resulting SolidCraft operation is a cut.
- The adapter decides the native representation. For Sample Plate it creates
  the editable `Holes` and `Bore` sketches and cut extrusions.
- Python scripts do not need an explicit `Sketch` object.

## Responsibility boundaries

```text
Python objects (SCPF)
  -> semantic compiler
  -> SolidCraft commands
  -> SolidCraft BRep, parameters and editable feature history
```

Never silently treat numeric coordinates as robust long-lived face
references. Native save/reopen and parameter-edit tests determine which
anchors are truly associative.
