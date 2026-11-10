# 06 — Verification

## Offline Rust checks

CI compiles the Rust crate, runs all Rust tests, generates the semantic plate command plan and compares it semantically with the reviewed [`examples/plate/solidcraftforge/solidcraft.json`](../examples/plate/solidcraftforge/solidcraft.json).

The fixture comparison deliberately treats JSON numbers such as `10` and `10.0` as equal.

## SolidCraft 0.30.1 runtime

The first native run exposed an invalid partial exact face pick. After changing the adapter to a **point-only face pick**, the pinned [SolidCraft 0.30.1 runtime workflow](https://github.com/brainboxemb/exp.2026-011.solidcraft/actions/runs/42671620051) succeeded.

Observed native model:

- 1 closed body named `Plate`;
- bounding box approximately **100 × 60 × 10 mm**;
- volume **57955.24872694561 mm³**;
- 14 reported faces: 8 cylindrical and 6 planar;
- both sketches solved;
- timeline contains Sketch → Extrude → Fillet → Sketch → Extrude;
- every timeline feature reports `error: null`;
- STEP and native `.sc` export succeeded;
- the native `.sc` stores the hole sketch as a real **face attachment** to `Plate`'s extrude cap;
- the saved workplane axes are X=(1,0,0), Y=(0,1,0), so its local coordinates align with the intended XY coordinates;
- the four saved circle centres are exactly (-35,-15), (35,-15), (35,15), (-35,15);
- a 1280 × 800 preview visibly shows four through-holes and rounded vertical outside corners.

The runtime workflow checks those measurements and the native face-attachment metadata automatically. It also rebuilds a script from the saved `.sc` history, then compares body count, volume and bounding box with the saved design.

This is strong evidence that the high-level box/fillet/top-face-holes example actually executes in SolidCraft 0.30.1. It is **not yet** proof of arbitrary topology selection or robust parametric editing.

## Still to qualify

- visually inspect the retained preview/STEP for the intended four hole positions and rounded outside vertical corners;
- change a named design parameter after save/reopen and confirm downstream rebuild;
- implement more general face/edge selectors without hard-coded base-box assumptions;
- GUI and MCP transports.


## Parametric edit qualification

The current SolidCraftForge Plate script promotes `length`, `width` and `thickness`
to named CAD-domain parameters. The SolidCraft adapter creates them with native `parameters.add` (explicit `mm` unit)
and uses their names in the base sketch and extrusion distances. Later edits use
`parameters.change` on those existing parameters.

The runtime workflow changes `thickness` from **10 mm to 15 mm** in the saved
native design and verifies that the body height, attached top-face workplane and
through-hole cut rebuild associatively. This specifically tests that the Rust CAD
abstraction produces an editable SolidCraft design rather than only a one-shot solid.


## SolidCraft face attachment after a parameter change

The saved `.sc` keeps the sketch plane's **authoring snapshot** at its original
Z=10 mm, but also stores a certified face anchor to the high cap of the base
extrusion. After changing `thickness` to 15 mm, the evaluated body is exactly
15 mm high and its volume changes from 57955.24872694561 to
86932.87309041845 mm³, while the model still reports 8 cylindrical faces and
6 planar faces.

So qualification must test the **topological anchor plus resulting geometry**,
not require the serialized authoring-plane coordinates themselves to be
rewritten. The runtime workflow now checks exactly that.
