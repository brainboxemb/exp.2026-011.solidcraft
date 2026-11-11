# HUB75 Panel — first native SolidCraft assembly experiment

Source of measured geometry: `brainboxemb/2026-006-01.cad.HUB75-display-frame`,
`v1.2/cad/components/hub75_panel.scad` (portrait 64×32 P5 panel).

This first SCPF model is **not** an exact reproduction of the panel.
It contains the measured front envelope **159.70 × 319.71 mm**,
a **14.50 mm** depth, and the six **Ø3 mm** mounting-hole centres:
**X=±72 mm**, **Y=-152/0/+152 mm**. It uses one grey housing material.
The original STEP-derived housing has a **real taper**: the outer perimeter
insets by **1.25 mm per side**, continuously from **Z=2.00 mm** (the start
of the rear housing) to **Z=14.50 mm**. The current plain rectangular
envelope does **not yet reproduce this sloping housing wall**. It must be
implemented as a drafted/lofted feature, not approximated with a short
edge chamfer. This is a known geometric gap before accepting the panel
model as a dimensional reference.

The more complex rear frame, PCB, connectors, pin guides and alternating
orientation are deliberately not modelled yet.

SCPF uses X for width, Y for height and Z for depth (front at Z=0).
The source OpenSCAD model used X/Z for the front and Y for depth.

The assembly builds the model **once**, then creates a second occurrence with
`panel.copy().move(x=160)`. `TwoHub75Panels()` therefore produces one
`Hub75Panel` component definition and two native occurrences at X=0 and
X=160 mm. A native occurrence
has its own position without duplicating the panel's editable geometry.
The gap between physical panel envelopes is **0.30 mm**, as in the
original 160 mm nominal placement grid.

**Current limit:** `copy().move(x=self.pitch_x)` uses a placement value,
not an associative SolidCraft constraint or an editable native design
parameter. Rotations, five occurrences, and the detailed body/PCB/connector
colors are separate follow-ups in issue #16.

Generate and inspect:

```powershell
$env:PYTHONPATH = "scpf"
python -m scpf examples/hub75-panel/scpf/model.py --out output/hub75.json
solidcraft-cli run output/hub75.json --param-check strict --results --save output/hub75.sc
```
