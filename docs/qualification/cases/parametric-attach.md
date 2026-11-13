# Parametric attachment gap

## Use scenario

A model author wants two components attached face-to-face but with an editable
distance along the attachment normal.

## Expected behaviour

The gap remains a native editable relationship. Changing it in the saved
SolidCraft design must move the child without rerunning Forge.

## Forge API

```python
block = Block().attach(
    base,
    parent=Anchor.RIGHT,
    child=Anchor.LEFT,
    gap=self.gap,
)
```

## Semantics

`gap` is a scalar distance along the attachment normal. It is not an XYZ
translation and not a planar offset.

## SolidCraft mapping

Forge emits a rigid native joint with the symbolic gap as the joint offset.

## Acceptance criteria

- initial gap is 10 mm;
- the child is on the correct side of the parent;
- no occurrence move is used to fake the parametric relationship.

## Parametric change

Change `gap` from 10 mm to 30 mm in the saved `.sc` design. The child must
move 20 mm farther along the same joint normal.

## Verification evidence

Fixture: `examples/parametric-attach/scpf/model.py`

Both pre-change and post-change native measurements are retained.

## Reference models

**BOSL2:** useful conceptual comparison for displacement along the local anchor
normal rather than a blind world-axis translation.
