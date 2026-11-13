# Face anchor follows parent geometry

## Use scenario

A child component is attached to the right face of a parent whose width is an
editable parameter.

## Expected behaviour

When the parent becomes wider, the child remains attached to the semantic
right face. The anchor must not freeze to the original absolute X coordinate.

## Forge API

```python
base = Base(width=self.base_width)
block = Block().attach(
    base,
    parent=Anchor.RIGHT,
    child=Anchor.LEFT,
)
```

## Semantics

A standard face anchor identifies a meaningful region of the parent geometry,
not a one-time coordinate calculation.

## SolidCraft mapping

Forge lowers the semantic face anchor to a native SolidCraft reference used by
the joint.

## Acceptance criteria

- the child initially touches the parent's right face;
- the native reference remains associated with that face.

## Parametric change

Change `base_width` from 40 mm to 80 mm in the saved design. The child must
follow the moved right face automatically.

## Verification evidence

Fixture: `examples/parametric-anchor/scpf/model.py`

## Reference models

**BOSL2:** cardinal anchors similarly describe a meaningful side of a parent
instead of an absolute coordinate.
