# Corner Bracket

SCPF port of the production OpenSCAD corner bracket in
`brainboxemb/2026-011-01.cad.model-archive`,
`models/corner_bracket/v0.1/scad/corner_bracket.scad`.

Reference commit: `bcb31e89cd6a0d185a99222d958e0dbe2b7b7a63`.

This is deliberately a **design port**, not a line-for-line translation of
OpenSCAD helper geometry.

## Source design

Default production geometry:

- 24 mm bracket width;
- 12 mm wall thickness;
- 60 × 60 mm arms;
- 6 mm outside-corner chamfer;
- 3 mm arm-end chamfers;
- 2 mm broad-side edge chamfer;
- 4 mm rounded inside corner;
- 0.6 mm elephant-foot relief;
- four M5 DIN 7991 countersunk bolt holes.

The OpenSCAD source describes the construction as:

```text
2D L profile
    ↓
outside side-chamfer keep envelope
    ↓
continuous elephant-foot side relief
    ↓
4 × M5 countersunk bolt cuts
    ↓
final bracket
```

## Coordinate convention

The production OpenSCAD bracket is defined in **world X/Z**, with the
horizontal arm extending toward **+X** and the vertical arm toward **−Z**.
SolidCraft 0.30.1's named `XZ` sketch maps the sketch's second coordinate
to **world −Z** (right-handed plane orientation). The Python model therefore
negates that sketch coordinate when creating `Polygon2D`. This keeps all
feature picks, bolt directions, and the expected
`[-12, -12, -60] → [60, 12, 12]` bounding box in **world coordinates**.

This matters: using the OpenSCAD X/Z points unchanged in a SolidCraft `XZ`
sketch mirrored the bracket and caused the first native chamfer to pick an
ambiguous vertex rather than the intended outer edge.

## SCPF history

SCPF keeps the same manufacturing intent but uses native CAD features where
OpenSCAD needs temporary hull/cutter geometry:

```text
Profile sketch
    ↓ symmetric extrude
Inside-corner fillet
    ↓
Outside side-edge chamfer
    ↓
Inside elephant-foot chamfer
    ↓
4 × recessed countersunk holes
    ↓
flat print-edge relief holes
```

The arm-end chamfers, outside-corner chamfer and the small elephant-foot bevels
on the two arm end faces remain part of the 2D polygon, matching the source.

The continuous 0.6 mm inside relief is represented by a native chamfer on the
tangent contact-edge chain. SolidCraft follows a tangent edge chain from one
edge pick, so one pick on each broad print face should cover:

```text
horizontal contact edge
        ↓
inside radius
        ↓
vertical contact edge
```

Native qualification must prove that this produces the intended valid BRep;
the mapping is not considered equivalent merely because the Python reads more
simply.

## Countersunk holes

The source has a 1 mm recessed DIN 7991 head, not a flush countersink.

For each main hole SCPF therefore keeps one semantic `Hole(...)`, while the
compiler lowers the recessed countersink to two native Hole features:

1. a cylindrical recess to `head_recess`;
2. a countersunk through-hole starting on that new floor.

The separate 0.2 mm flat print-edge reliefs remain shallow simple holes on the
outside and inside openings.

The default bolt centres remain 24 mm and 42 mm from the inner-corner
reference on each arm.
