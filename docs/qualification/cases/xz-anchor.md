# Corner anchors on an XZ-profile extrusion

## Use scenario

A board is authored as a rectangular XZ polygon and extruded through Y. Child
components must attach to both top-front corners and keep following them when
the board dimensions change.

## Expected behaviour

Standard semantic corner anchors work regardless of whether the rectangular
part originated from the usual XY Box path or an XZ sketch/extrusion.

## Forge API

```python
profile = Polygon2D(points, plane="XZ", world=True)
board = profile.extrude(depth, direction=Direction.POSITIVE)

right = Marker().attach(
    board,
    parent=Anchor.FRONT_TOP_RIGHT,
    child=Anchor.BACK_TOP_RIGHT,
)
left = Marker().attach(
    board,
    parent=Anchor.FRONT_TOP_LEFT,
    child=Anchor.BACK_TOP_LEFT,
)
```

## Semantics

Mirrored corners are an important check that Forge does not assume one global
direction for every anchor. The parent anchor's local frame/topology matters.

## SolidCraft mapping

Forge resolves each corner to native topology references on the XZ-extruded
board and creates native joints.

## Acceptance criteria

- left and right markers attach to different mirrored corners;
- both references remain associated with the board after dimension edits.

## Parametric change

Change the board from 40 × 20 mm to 80 × 40 mm in the saved design. Both
markers must follow their respective corners.

## Verification evidence

Fixture: `examples/xz-anchor/scpf/model.py`

## Reference models

**OpenSCAD:** the shape itself resembles `polygon()` plus
`linear_extrude()`.

**BOSL2:** mirrored anchors demonstrate why a local attachment frame is a more
useful abstraction than a single assumed world direction.
