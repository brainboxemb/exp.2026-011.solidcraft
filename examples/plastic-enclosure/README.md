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
enclosure = Box(self.length, self.width, self.height)
enclosure = enclosure.shell(self.wall, open=Faces.TOP)

enclosure = enclosure + Lip(width=1, height=2).at(...)
enclosure = enclosure + SnapFit(...).at(...)
enclosure = enclosure + Boss(d=7, h=12, hole_d=2.5).at(...)
enclosure = enclosure + Boss(d=7, h=12, hole_d=2.5).at(...)
enclosure + Rest(width=16, length=24, height=3).at(...)
```

`Faces.TOP` is a face selector for `shell()`. It is deliberately separate
from `Anchor.TOP`, which describes relative placement for `attach()`.

SCPF `Box` is centered in X/Y, while the uploaded SolidCraft source uses a
corner at `[0, 0, 0]`. The feature pick coordinates are therefore translated
by `[-40, -25, 0]`; the enclosure dimensions and relative feature locations
remain the same.

The native CI qualification verifies the saved feature sequence and names,
checks that the resulting body is closed, and explicitly checks that no
sketches were created.
