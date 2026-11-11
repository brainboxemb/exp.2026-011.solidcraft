# HUB75 Panel — first native SolidCraft assembly experiment

Source of measured geometry: `brainboxemb/2026-006-01.cad.HUB75-display-frame`,
`v1.2/cad/components/hub75_panel.scad` (portrait 64×32 P5 panel).

This first SCPF model is **not** an exact reproduction of the panel.
It contains the measured front envelope **159.70 × 319.71 mm**,
a **14.50 mm** depth, and the six **Ø3 mm** mounting-hole centres:
**X=±72 mm**, **Y=-152/0/+152 mm**. It uses one grey housing material.
The more complex rear frame, PCB, connectors, pin guides and alternating
orientation are deliberately not modelled yet.

SCPF uses X for width, Y for height and Z for depth (front at Z=0).
The source OpenSCAD model used X/Z for the front and Y for depth.

`TwoHub75Panels()` creates one `Hub75Panel` component definition and
two native occurrences placed at X=0 and X=160 mm. A native occurrence
has its own position without duplicating the panel's editable geometry.
The gap between physical panel envelopes is **0.30 mm**, as in the
original 160 mm nominal placement grid.

**Current limit:** `move(x=self.pitch_x)` is a placement value,
not an associative SolidCraft constraint or an editable native design
parameter. Rotations, five occurrences, and the detailed body/PCB/connector
colors are separate follow-ups in issue #16.

Generate and inspect:

```powershell
$env:PYTHONPATH = "scpf"
python -m scpf examples/hub75-panel/scpf/model.py --out output/hub75.json
solidcraft-cli run output/hub75.json --param-check strict --results --save output/hub75.sc
```
