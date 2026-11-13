# Corner anchor follows width and height

## Use scenario

A model author wants a child attached to the front-top-right corner of a
rectangular parent. Both parent width and height may change later.

## Expected behaviour

The child follows the same semantic corner after either dimension changes.

## Forge API

```python
marker = Marker().attach(
    base,
    parent=Anchor.FRONT_TOP_RIGHT,
    child=Anchor.BACK_TOP_RIGHT,
)
```

## Semantics

A corner anchor is more than a point. For reliable attachment it must identify
stable parent topology and a meaningful local attachment orientation.

## SolidCraft mapping

Forge lowers the rectangular corner to native topology-backed edge/face/corner
references used by `joint.create`.

## Acceptance criteria

- the marker starts on the intended corner;
- width changes move it horizontally with the corner;
- height changes move it vertically with the corner;
- no frozen absolute placement is used.

## Parametric change

Change the parent from 40 × 20 mm to 80 × 40 mm in the saved design. The
marker must follow both changed dimensions.

## Verification evidence

Fixture: `examples/corner-anchor/scpf/model.py`

## Reference models

**BOSL2:** edge and corner anchors are a useful conceptual reference. BOSL2
also makes anchor orientation explicit, which is important for Forge's future
anchor/frame design.
