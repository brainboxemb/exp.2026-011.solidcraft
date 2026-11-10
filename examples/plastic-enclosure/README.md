# Plastic Enclosure

Reverse-engineering example for the supplied SolidCraft **Plastic Enclosure** design.

## Original history

The source design is kept unchanged at
[`source/plastic-enclosure.json`](source/plastic-enclosure.json).

Its saved SolidCraft feature history is:

1. `Box1` — 80 × 50 × 30 mm
2. `Shell1` — 2 mm wall, top face open
3. `Lip1` — 1 mm wide × 2 mm high
4. `SnapFit1` — 14 mm cantilever snap
5. `Boss1` — Ø7 × 12 mm with Ø2.5 mm hole
6. `Boss2` — same boss at the opposite corner
7. `Rest1` — 16 × 24 × 3 mm support

The original SolidCraft history contains **no sketches**.

## SCPF model

[`scpf/model.py`](scpf/model.py) keeps the same object-level meaning:

```python
class Enclosure:
    length = 80.0
    width = 50.0
    height = 30.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.length, self.width, self.height)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        snap = SnapFit(...).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
            offset=(X.CENTER, Y.MAX - 6),
        )
        enclosure = enclosure + snap

        boss = Boss(...).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
            offset=(X.MIN + 10, Y.MIN + 10),
        )
```

`Faces.TOP` is a face selector for `shell()`. It is deliberately separate
from `Anchor.TOP`, which describes relative placement for `attach()`.

SCPF `Box` is centered in X/Y, while the uploaded SolidCraft source uses a
corner at `[0, 0, 0]`. The script does not manually compensate with
`length / 2` or `width / 2`: `X.MIN/CENTER/MAX` and `Y.MIN/CENTER/MAX`
keep each coordinate relative to the matching enclosure axis.

The uploaded SolidCraft source contains no sketches. SCPF deliberately keeps
its normal `Box` representation instead: one footprint sketch plus an
extrusion, followed by the native Shell/Lip/SnapFit/Boss/Rest features.

The native CI qualification verifies that history, checks that the resulting
body is closed, and checks that exactly one base sketch is present.
