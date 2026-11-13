# Named oriented AnchorFrame

## What this case is about

Sometimes a face such as `TOP` or `RIGHT` is enough to attach one part to
another. Sometimes it is not. A bracket, connector or screw hole can have its
own meaningful mounting point and its own orientation.

For that situation Forge uses an `AnchorFrame`. You can think of it as a
small local coordinate system attached to the component.

An AnchorFrame answers three simple questions:

1. **Where is the attachment point?** — `origin`
2. **Which way does the attachment point face?** — `z`
3. **Which way is “up” around that direction?** — `x`

The third axis does not need to be supplied. Once Z and X are known, the full
local frame is determined.

## The six easy directions

For ordinary axis-aligned parts, you do not need to write vectors by hand:

| Forge | Vector | Meaning |
| --- | --- | --- |
| `RIGHT` | `(1, 0, 0)` | +X |
| `LEFT` | `(-1, 0, 0)` | -X |
| `BACK` | `(0, 1, 0)` | +Y |
| `FRONT` | `(0, -1, 0)` | -Y |
| `UP` | `(0, 0, 1)` | +Z |
| `DOWN` | `(0, 0, -1)` | -Z |

These names are only readable unit vectors. They do not introduce another
rotation system. Arbitrary XYZ vectors remain available when a frame is not
aligned to the main axes.

## Forge API

The arm publishes a named attachment point called `tip`:

```python
def anchors(self):
    return {
        "tip": AnchorFrame(
            origin=(20, 0, 5),
            z=RIGHT,
            x=UP,
        ),
    }
```

Read that literally:

- the attachment point is at local position `(20, 0, 5)`;
- its local Z axis points to the right;
- its local X axis points upward.

The marker publishes the mating frame:

```python
def anchors(self):
    return {
        "mount": AnchorFrame(
            origin=(0, 0, 5),
            z=LEFT,
            x=UP,
        ),
    }
```

The two components are then connected by name:

```python
marker = Marker().attach(
    arm,
    parent="tip",
    child="mount",
)
```

## What should happen

The complete arm occurrence is rotated 90 degrees around global Z. The
important point is that `tip` belongs to the arm, so its local coordinate
frame rotates with the arm.

The marker must therefore remain attached to the arm tip and keep the
orientation defined by the two local frames. Forge must not recalculate the
tip as a frozen world-space XYZ position.

## How Forge maps this to SolidCraft

`AnchorFrame` is the Forge concept. SolidCraft still owns the actual
occurrence placement and joint solution.

For an explicitly rotated occurrence, Forge uses the native joint-origin path
so that SolidCraft applies the occurrence transform to the authored local
frame. The public Forge model remains just:

```text
origin + Z direction + X direction
```

The generated SolidCraft commands are an implementation detail of that
contract.

## Acceptance criteria

- the parent occurrence can rotate independently;
- the named `tip` frame rotates with the parent;
- the marker is solved at that rotated frame;
- the marker orientation follows the authored Z and X directions;
- the generated native model contains no Forge-side hard-coded world position
  for the rotated tip.

## Parametric change

No dimension mutation is required in this case. This fixture isolates one
question: does a named local frame retain its meaning when its occurrence is
rotated?

## Verification evidence

Fixture: `examples/custom-anchor/scpf/model.py`

## Reference model

**BOSL2** uses the same general idea: an anchor is more than a point. It has a
position and a local orientation. BOSL2 expresses the rotation around the
anchor normal with `spin`; Forge instead keeps the local frame explicit with
Z and X directions.
