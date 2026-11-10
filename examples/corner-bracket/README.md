# Corner Bracket — SCPF

The default `scpf/model.py` is the **fast four-hole version**, using one native countersink per bolt. It avoids the coincident faces and repeated Boolean retries of the earlier recessed/countersunk-hole reconstruction.

The original 42-command experiment is retained as `scpf/model_reference.py`. It is **not used as the default**. The fast countersink has a larger tapered opening and does not reproduce the original flat-bottom head recess or the tiny 0.2 mm hole-edge reliefs exactly.

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
