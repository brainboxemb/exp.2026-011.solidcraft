# Python CAD API design

SCPF exposes CAD objects, not JSON commands, transports, or an independent
geometry engine.

## User-facing model

```python
@dataclass
class SamplePlate:
    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges=Edges.VERTICAL)

        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=self.width - 24, axis=Axis.X
        ).on(plate, Anchor.TOP)
        plate = plate + holes

        boss = Cylinder(d=24, h=14).attach(
            plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
        plate = plate + boss

        bore = Hole(d=12, depth=Depth.THROUGH_ALL).on(plate, Anchor.TOP)
        plate + bore

SamplePlate()
```

## Semantics

- `Cylinder` represents 3D material or a Boolean cutter.
- `Hole` is a native CAD feature. `plate + hole` means add the feature;
  native `solid.hole` removes material.
- `.attach()` aligns parent and child anchors; `.on()` places an object
  on a face. Supported placements are intentionally limited.
- `Rectangle2D(...).extrude()` and attached `Cylinder` may generate
  internal sketch and extrusion commands. Python does not require an
  explicit `Sketch` object.
- The resulting SolidCraft history can differ from the original sample's
  sketch-based history while representing equivalent design intent.

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
