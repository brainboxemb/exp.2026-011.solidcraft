# Python CAD API design

SCPF exposes CAD objects, not JSON commands, transports, or an independent
geometry engine.

## User-facing model

A model does not need `@dataclass`. Numeric class fields are model
parameters:

```python
class Enclosure:
    length = 80.0
    width = 50.0
    height = 30.0
    wall = 2.0
```

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
- `Faces` selects geometry for operations; `Anchor` describes relative
  placement. They are intentionally separate concepts.
- `shell()` is a modifier like `fillet()`: for example
  `body.shell(2, open=Faces.TOP)`.
- `Lip`, `SnapFit`, `Boss` and `Rest` are ordinary object-level
  building blocks, like `Box`, `Cylinder` and `Hole`; the compiler maps
  them to native SolidCraft plastic features.
- `Anchor.INNER_BOTTOM` refers to the inner floor of a shelled body,
  so enclosure details can be placed relative to the shell wall instead of
  hard-coded world Z coordinates.
- `Bounds.MIN`, `Bounds.CENTER` and `Bounds.MAX` describe X/Y
  placement relative to the parent bounds, for example
  `offset=(Bounds.MIN + 10, Bounds.MAX - 6)`.

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
