# Face-relative hole pattern

## Use scenario

A model author wants two through holes on the top face of a plate, spaced
symmetrically along one axis.

## Expected behaviour

The holes are expressed as hole features related to a selected face, not as
arbitrary subtraction cylinders positioned by hand.

## Forge API

```python
with Sketch(plane="XY") as sketch:
    Rectangle2D(width, depth)
plate = sketch.extrude(thickness)
holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
    count=2, spacing=spacing, axis=Axis.Y
).on(plate, face=Faces.TOP)
plate + holes
```

## Semantics

`Faces.TOP` identifies the parent surface for a within-component feature.
This is distinct from assembly `Anchor` semantics.

## SolidCraft mapping

Forge emits native sketch/extrude geometry and native hole/pattern placement
commands.

## Acceptance criteria

- one plate body exists;
- two through holes exist at the requested spacing;
- no native timeline errors occur.

## Parametric change

No saved-design mutation is required for this base feature-placement case.

## Verification evidence

Fixture: `examples/anchored-holes/scpf/model.py`

## Reference models

**OpenSCAD:** comparable geometry commonly uses `difference()` plus repeated
cylinders. Forge intentionally expresses manufacturing intent through native
SolidCraft hole features.
