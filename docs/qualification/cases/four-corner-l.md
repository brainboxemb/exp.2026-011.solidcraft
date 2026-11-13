# One L-profile on all four front corners

## Use scenario

Before testing a changing frame size, we need to prove the simpler statement:
one directional L-shaped child can be placed at all four corners of a fixed
rectangular parent and each corner gives the child the correct in-plane
orientation.

This isolates corner-frame semantics from parameter mutation, gap/normal
offsets and the larger HUB75 assembly.

## Geometry

The parent is a fixed 120 × 30 × 80 mm block.

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
    z=(0, -1, 0),
    x=(1, 0, 0),
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

## Q5 — intentionally not yet

No dimensions change in this case. Only after these four fixed placements are
correct do we add a second qualification step that edits parent width/height in
the saved SolidCraft design and verifies that all four brackets follow.

This separation tells us whether a failure comes from initial corner
orientation or from later associativity.

## Q6 — visual evidence

The native snapshot is retained because an L-profile makes mirrored/rotated
corner mistakes visually obvious.

## Reference models

**BOSL2:** useful for the expectation that a reusable child-local frame can be
attached through different semantic parent anchors.

**SolidCraft:** the native corner origin is topology-backed by the face, edge
and selected corner; its local frame is what should give each occurrence its
different clock position.
