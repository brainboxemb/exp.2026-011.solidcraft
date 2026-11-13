# Minimal L-profile reference component

## Use scenario

Assembly tests need a visually obvious L-shaped component whose geometry is so
simple that placement/orientation errors cannot be confused with holes,
fillets, shells or other features.

## Expected behaviour

Forge creates one clean L profile and extrudes it symmetrically. This component
can then be reused by later anchor and orientation scenarios.

## Forge API

```python
profile = Polygon2D(points, plane="XZ")
return profile.extrude(width, direction=Direction.SYMMETRIC)
```

## Semantics

This is intentionally a **geometry baseline**, not yet an attachment API case.

## SolidCraft mapping

Forge emits a native XZ sketch/polygon followed by a symmetric extrusion.

## Acceptance criteria

- the L has the requested 40 mm outer arm length;
- both legs are 12 mm thick;
- extrusion width is 24 mm and symmetric;
- no unrelated features exist.

## Parametric change

Not part of this baseline case. Later assembly cases reuse the component and
qualify anchor/frame/offset behaviour independently.

## Verification evidence

Fixture: `examples/bracket/scpf/model.py`

## Reference models

**OpenSCAD:** equivalent baseline is an L-shaped 2D polygon followed by
`linear_extrude(center=true)`.

**BOSL2:** later attachment cases can reuse the simple shape while comparing
anchor/orient semantics independently of bracket feature complexity.
