# Editable local offset at an attachment

## Use scenario

A model author wants an attached component shifted within the local plane of a
corner attachment, while keeping that shift editable.

## Expected behaviour

The offset follows the local attachment frame. It must not silently be treated
as world X/Y coordinates.

## Forge API

```python
marker = Marker().attach(
    base,
    parent=Anchor.FRONT_TOP_RIGHT,
    child=Anchor.BACK_TOP_RIGHT,
    offset=(0, -self.shift),
)
```

## Semantics

The current two-value `offset=(u, v)` is a **local planar offset** in the
joint frame.

This distinction is critical:

- `gap` — local normal distance;
- `offset=(u,v)` — local in-plane displacement;
- world XYZ translation is a different concept and must not be inferred from
  either of these.

## SolidCraft mapping

Forge lowers a non-zero or symbolic planar offset to a native planar joint and
passes the values as the joint's local planar values.

## Acceptance criteria

- the marker moves along the intended local axis;
- mirrored/corner orientation does not redefine the API as world X/Y;
- the expression remains symbolic in SolidCraft.

## Parametric change

Change `shift` from 5 mm to 10 mm in the saved design. The marker must move
another 5 mm along the same local joint axis.

## Verification evidence

Fixture: `examples/parametric-offset/scpf/model.py`

## Reference models

**BOSL2:** particularly relevant. Attachment operations are interpreted in the
local coordinate system at the parent anchor.

**OpenSCAD:** a raw `translate([x,y,z])` is not equivalent; that is an explicit
object/world transform rather than a local joint relationship.
