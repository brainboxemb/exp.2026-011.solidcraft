# Python CAD API design

SCPF exposes CAD objects, not JSON commands, transports, or an independent
geometry engine.

## User-facing model

The default Sample Plate reproduces the four original sketch-based features:

```python
plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
plate = plate.fillet(6, edges=Edges.VERTICAL)
holes = Circle2D(d=8).at(12, self.depth / 2) + Circle2D(d=8).at(
    self.width - 12, self.depth / 2)
plate = plate.cut(holes.extrude(self.thickness), name="Holes")
boss = Circle2D(d=24).at(self.width / 2, self.depth / 2, self.thickness)
plate = plate.add(boss.extrude(14), name="Boss")
bore = Circle2D(d=12).at(
    self.width / 2, self.depth / 2, self.thickness + 14)
plate.cut(bore.extrude(self.thickness + 14, direction=Direction.NEGATIVE),
          name="Bore")
```

The alternative native Hole version is shorter:

```python
plate = plate.add(
    Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
        count=2, spacing=self.width - 24, axis=Axis.X),
    on=Anchor.TOP)
plate = plate.add(Cylinder(d=24, h=14), on=Anchor.TOP)
plate = plate.add(Hole(d=12, depth=Depth.THROUGH_ALL), on=Anchor.TOP)
```

## Semantics

- `part.add(feature, on=Anchor.TOP)`: position and apply the feature in one
  operation; the target is not repeated in the script.
- `part.add(feature, at=(x, y, z))`: place it at an explicit world point.
- `part.cut(cutter, name="Bore")`: subtract a sketch-based or solid cutter;
  the optional name labels the generated feature/sketch where supported.
- Native `Hole` removes material even though it is added as a CAD feature.
- `.on()` / `.attach()` and Python `+` / `-` remain available for
  lower-level composition and compatibility, but are not needed for typical
  feature additions.
- A `Circle2D` profile cut creates an editable sketch and cut feature.
  A native `Hole` creates a Hole feature without a corresponding sketch.
- The adapter creates all necessary internal sketches. Python scripts do not
  need an explicit `Sketch` object.

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
