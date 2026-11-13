# One L-profile on all four front corners

## Use scenario

The case is deliberately verified in two phases. First, one directional
L-shaped child must be correct at all four corners of the baseline parent.
Only after that baseline is proven do we edit the saved native parent width
and height and verify that the same four topology-backed relationships follow.

This isolates corner-frame semantics from gap/normal offsets and the larger
HUB75 assembly while still proving saved-design associativity.

## Geometry

The parent starts as a 120 × 30 × 80 mm block. Width and height are public
editable component parameters; depth remains a fixed constant.

The child uses the same deliberately simple L-profile as the minimal L
qualification baseline:

- 40 mm outer extent in X;
- 40 mm outer extent in Z;
- 12 mm arm thickness;
- 24 mm symmetric extrusion width.

In its neutral local position the L occupies +X and -Z from its origin.

## Forge API

Every occurrence uses the same child frame:

```python
mount = AnchorFrame(
    origin=(0, 0, 0),
    z=FRONT,
    x=RIGHT,
)
```

Only the parent corner changes:

```python
Anchor.FRONT_TOP_LEFT
Anchor.FRONT_TOP_RIGHT
Anchor.FRONT_BOTTOM_RIGHT
Anchor.FRONT_BOTTOM_LEFT
```

There is deliberately no `gap`, `offset` or parameter mutation. The attachment uses `angle=0` explicitly so SolidCraft does not choose a half-turn from the starting placement.

## Expected behaviour

The parent corner frame should rotate the same neutral L into four different
clock positions.

Looking at the front face, the four child bounding boxes must be:

```text
top-left:     X -60 .. -20   Z 40 .. 80
top-right:    X  20 ..  60   Z 40 .. 80
bottom-right: X  20 ..  60   Z  0 .. 40
bottom-left:  X -60 .. -20   Z  0 .. 40
```

The L is extruded symmetrically through 24 mm. With its centre plane on the
parent front face at Y=-15, every bracket spans Y=-27 .. -3.

This case is about local corner orientation only; the bracket intentionally
straddles the face. Normal/front-back placement is qualified separately later.

## Resolved native frame cycle

On SolidCraft 0.30.1 the four parent corner frames resolve with the same
front-face normal `z=(0,-1,0)`, while the in-plane X direction rotates around
the corners in this order:

```text
top-left:     x=( 0, 0,-1)
top-right:    x=(-1, 0, 0)
bottom-right: x=( 0, 0, 1)
bottom-left:  x=( 1, 0, 0)
```

The child resolves with the opposite mating normal `z=(0,+1,0)` and the same
in-plane X direction as its parent frame. This is why one child frame
`z=(0,-1,0), x=(1,0,0)` plus explicit `angle=0` works at every corner:
the parent anchor supplies the four clock positions.

## Q1/Q2 — command contract

The generated command JSON must contain:

- one `FrameBlock` component;
- one shared `LBracket` component definition;
- four L occurrences (one original plus three copies);
- four rigid joints;
- four different topology-backed parent corner origins;
- the same child `point/z/x` frame on all four occurrences;
- explicit `angle=0` on all four joints;
- no gap/offset values.

## Q3/Q4 — native SolidCraft

SolidCraft must build five bodies with no timeline errors. Native measurements
must match the parent and four expected bracket bounding boxes above.

## Q5 — saved-design parent scaling

After the baseline passes, the native saved design is edited without rerunning
the Python model:

```text
FrameBlock_width:  120 -> 160 mm
FrameBlock_height:  80 -> 120 mm
```

Expected parent bounds become X=-80..80 and Z=0..120. The four L bounds become:

```text
top-left:     X -80 .. -40   Z 80 .. 120
top-right:    X  40 ..  80   Z 80 .. 120
bottom-right: X  40 ..  80   Z  0 ..  40
bottom-left:  X -80 .. -40   Z  0 ..  40
```

A second `joint.inspect` must show the origins moved to those new corners
while the same four parent-X directions and mating normals remain intact.
This proves the native topology relationship, not a Python-side recalculation.

## Q6 — visual evidence

The native snapshot is retained because an L-profile makes mirrored/rotated
corner mistakes visually obvious.

## Reference models

**BOSL2:** useful for the expectation that a reusable child-local frame can be
attached through different semantic parent anchors.

**SolidCraft:** the native corner origin is topology-backed by the face, edge
and selected corner; its local frame is what should give each occurrence its
different clock position.
