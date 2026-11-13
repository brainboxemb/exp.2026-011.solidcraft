# Rigid component attachment

## Use scenario

A model author has one reusable block definition and wants a second occurrence
attached directly to the right-hand face of the first.

## Expected behaviour

Both occurrences share one component definition. The second occurrence is
positioned by an attachment relationship, not by duplicating geometry or
hard-coding an unrelated world coordinate.

## Forge API

```python
left = Block()
right = Block().attach(
    left,
    parent=Anchor.RIGHT,
    child=Anchor.LEFT,
)
return left + right
```

## Semantics

An assembly attachment relates a **parent anchor** to a **child anchor**.
For this case both anchors are standard semantic faces.

## SolidCraft mapping

Forge creates one reusable component definition, copies an occurrence and emits
a native rigid `joint.create` between the selected references.

## Acceptance criteria

- exactly one shared component definition is used;
- two occurrences exist;
- the occurrences touch face-to-face;
- the joint is native and rigid.

## Parametric change

This base case has no mutation. A moving parent face is qualified separately.

## Verification evidence

Fixture: `examples/components/scpf/model.py`

## Reference models

**BOSL2:** conceptually similar to attaching a child anchor to a parent anchor.
The important common idea is that the relationship is expressed in terms of
meaningful attachment references rather than unrelated world coordinates.
