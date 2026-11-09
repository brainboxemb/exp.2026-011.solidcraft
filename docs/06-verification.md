# 06 — Verification

## Offline Rust checks

CI compiles the Rust crate, runs all Rust tests, generates the semantic plate command plan and compares it semantically with [`fixtures/plate-top-face.json`](../fixtures/plate-top-face.json).

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
- a 1280 × 800 preview was rendered by SolidCraft's CPU renderer.

The current runtime workflow also checks those basic measurements automatically and rebuilds a script from the saved native `.sc` history, then compares its evaluated body count, volume and bounding box with the saved design.

This is strong evidence that the high-level box/fillet/top-face-holes example actually executes in SolidCraft 0.30.1. It is **not yet** proof of arbitrary topology selection or robust parametric editing.

## Still to qualify

- visually inspect the retained preview/STEP for the intended four hole positions and rounded outside vertical corners;
- change a named design parameter after save/reopen and confirm downstream rebuild;
- implement more general face/edge selectors without hard-coded base-box assumptions;
- GUI and MCP transports.
