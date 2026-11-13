# Named oriented AnchorFrame

## Use scenario

A reusable component needs an application-meaningful attachment location that
is not one of the standard faces or corners, and the attachment also requires a
specific orientation.

## Expected behaviour

The component can publish a named local attachment frame. If the occurrence is
rotated, that frame rotates with the component.

## Forge API

```python
def anchors(self):
    return {
        "tip": AnchorFrame(
            origin=(20, 0, 5),
            z=(1, 0, 0),
            x=(0, 0, 1),
        ),
    }

marker = Marker().attach(arm, parent="tip", child="mount")
```

## Semantics

`AnchorFrame` is explicitly a **local coordinate frame**:

- `origin` — position in component-local coordinates;
- `z` — attachment normal/direction;
- `x` — orientation around that normal.

It is not merely a named point.

## SolidCraft mapping

Forge lowers the named frame to a native joint origin/reference while leaving
occurrence rotation to SolidCraft.

## Acceptance criteria

- the parent occurrence may rotate independently;
- the named frame follows that rotation;
- the child is placed at the rotated frame with the expected orientation.

## Parametric change

No parameter mutation is required; this case isolates frame orientation and
occurrence rotation.

## Verification evidence

Fixture: `examples/custom-anchor/scpf/model.py`

## Reference models

**BOSL2:** this is the closest conceptual reference. BOSL2 anchors combine
position with local orientation information used during attachment.
