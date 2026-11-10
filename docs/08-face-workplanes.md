# 08 — Semantic faces and workplanes

## Why this matters

Until now, the CAD API hid SolidCraft command names but placed holes by
creating an XY sketch at an **absolute Z offset**. A CAD API should be
able to say which *face* carries a sketch. CadQuery's workplanes are
an inspiration for this behavior.

## The implemented semantic API

```rust
let plate = Part::box3d(100.0, 60.0, 10.0)?
    .named("Plate")
    .faces(Faces::Top).workplane()
    .circle(-35.0, -15.0, 8.0)?
    .circle( 35.0,  15.0, 8.0)?
    .cut_through()?;
```

This is **real source code** in the experimental domain model, rather
than proposed pseudocode. The user never names a native SolidCraft
command or supplies a world-space face-picking point.

## What the adapter does

SolidCraft's current
[command reference](https://docs.solidcraft.io/reference/commands.html)
documents `sketch.create` with a face source:

```json
{"command": "sketch.create", "params": {
  "plane": {"face": [0.0, 0.0, 10.0]},
  "name": "Plate top-face holes"
}}
```

The adapter knows the original centered box is at Z=0..H and chooses
its upper face's center as the native reference point.

The first live SolidCraft 0.30.1 run showed that adding a body name
without a face index is invalid: an exact pick requires both. We therefore
use a **point-only** pick for this deliberately simple single-body model.
SolidCraft is responsible for resolving that unique planar face and
capturing the attachment. We do not guess a face index.
The adapter then draws the circular profiles, finishes the sketch and
uses a subtractive extrusion to form the holes.

The new face attachment is *a better reference than a free-floating plane*,
but the adapter still has no general topology query.

## Strict limits

- `Faces::Top` refers only to the **original** upper planar face of
  an axis-aligned base box. It is not yet a generic `faces(">Z")`
  selector for arbitrary models.
- A second top-face cut is rejected: an earlier hole could have
  removed the face point used to identify the target face.
- The adapter assumes the chosen top face's sketch axes align with
  the specified 2D hole coordinates. We must verify this against the
  actual SolidCraft GUI/CLI; the offline tests cannot prove it.
- Feature ordering matters. The example fillets the four original
  outside upright box edges before placing the holes.
- General edge/face identity, body placement, arbitrary workplanes and
  named topology are future qualification work.

## How to test it on Windows

The official Windows installer places
`solidcraft-cli.exe` beside `solidcraft.exe`, normally under
`C:\Program Files\SolidCraft`; see the
[official MCP guide](https://docs.solidcraft.io/guide/mcp.html).

From the repository root:

```powershell
.\scripts\qualify-solidcraft.ps1 -SkipBuild -Snapshot   # use checked fixture; no Rust required
.\scripts\qualify-solidcraft.ps1 -Snapshot              # additionally compile and test Rust
```

Without `-SkipBuild`, this builds/tests the Rust API and generates `output/examples/plate/scrf/solidcraft.json`; with `-SkipBuild`, it uses the committed and CI-checked SCRF command plan. It then
uses the real SolidCraft CLI with **strict parameter checking**, exports
`cad-plate.step` and the native `cad-plate.sc` design, and records
measurements/results. Output stays in ignored `output/`.

An accepted export does **not** prove the intended geometry: inspect
the STEP, hole positions, fillets, and editable native feature history.
Capture command output and SolidCraft version with any failures.

**Status:** the first actual SolidCraft 0.30.1 runtime test exposed the
invalid partial exact pick. The adapter now emits a point-only face pick;
the pinned runtime workflow must confirm whether the corrected model
executes and produces the intended geometry.
