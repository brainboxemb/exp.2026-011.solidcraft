# Corner Bracket — SCPF

The default `scpf/model.py` is the **fast four-hole version**, using one native countersink per bolt. It avoids the coincident faces and repeated Boolean retries of the earlier recessed/countersunk-hole reconstruction.

The original 42-command experiment is retained as `scpf/model_reference.py`. It is **not used as the default**. The fast countersink has a larger tapered opening and does not reproduce the original flat-bottom head recess or the tiny 0.2 mm hole-edge reliefs exactly.

## Named profile and explicit reliefs

The L outline is defined **once**, in a single `Polygon2D` table of `("name", (x, z))` rows:

```python
profile = Polygon2D([
    ("o_hor_tip", (h, 0)),
    ("o_hor_bevel", (h, w - end)),
    # ... the rest of the contour ...
    ("v_tip", (0, -v)),
    ("i_corner", (0, 0)),
], plane="XZ", world=True)
```

The name belongs to the **vertex** and becomes the sketch-line ID for the **segment beginning at that vertex**. `world=True` means the XZ coordinates are ordinary world (x, z); SCPF performs SolidCraft's local-sketch axis conversion.

`Edges.from_profile("o_*")` selects named profile segments on the two broad faces. `Edges.from_vertices("o_hor_tip", "v_tip")` instead selects the extrusion-direction edges starting at those vertices. SCPF translates both selectors to edge-pick points because SolidCraft 0.30.1's fillet/chamfer commands do not directly accept sketch-line IDs.

The original 0.6 mm **tip elephant-foot cuts are not in the polygon**: a separate native chamfer removes them at the two tip edges. Another chamfer produces the relief along the inside horizontal edge. The inside fillet, both reliefs, side chamfers, and holes remain separate editable features.

Named-edge selection is currently implemented for **symmetric XZ polygon extrusions only**. The remaining irregularities at the arm tips are a separate follow-up in issue #20.

For local GUI testing from the repository root:

```powershell
$env:PYTHONPATH = "scpf"
python -m scpf examples/corner-bracket/scpf/model.py --connect
```

Open an empty SolidCraft document and enable external Assistant control before running. To generate commands without touching the GUI:

```powershell
python -m scpf examples/corner-bracket/scpf/model.py --out output/corner-bracket.json
```

The uncorrected small pointed corners at the arm ends are tracked separately in [issue #20](https://github.com/brainboxemb/exp.2026-011.solidcraft/issues/20). This issue is intentionally deferred, not a blocker for this initial SCPF model.

Original geometry reference: `brainboxemb/2026-011-01.cad.model-archive`, `models/corner_bracket/v0.1/scad/corner_bracket.scad`.
