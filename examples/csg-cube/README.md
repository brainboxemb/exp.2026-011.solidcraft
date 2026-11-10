# CSG cube API comparison

This example is deliberately small: one size argument, primitive solids and boolean
operations. It is intended to compare **modeling syntax**, not geometry engines.

All variants describe the same intent:

1. intersect a sphere with a cube;
2. create three orthogonal cylinders;
3. subtract the cylinders from the body;
4. use a nominal size of 50 mm.

## Variants

- `scrf/model.rs` — the SCRF Rust script. It defines
  the reusable `CsgCube` type and ends with `CsgCube::new(50.0)`.
  There is no `main()`, `show()`, `build!()` or transport code in the script.
- `scrf/solidcraft.json` — the reviewed raw SolidCraft command
  sequence generated from that script.
- `microcad/model.mu` — µcad reference. µcad is its own Rust-inspired CAD
  language; this file is **not Rust**.
- `vcad/model.rs` — vcad's Rust BRep-kernel API.
- `cadquery/model.py` — CadQuery's Python API.
- `pythonscad/model.py` — PythonSCAD's lightweight Python object/CSG API,
  included because its object-style modeling syntax is a useful ergonomics
  reference.

The reference implementations are design comparisons only. Experiment 011 still
uses SolidCraft as its geometry engine.

Execution, export and measurement plumbing belongs in CI runners, not in the
model files.

## Script shape

SCRF scripts use ordinary Rust types. The final expression is the
object to build. The Cargo example harness wraps that expression outside the
script only so normal Rust can compile and test it.

## Tested versions

- Experiment 011: current branch implementation
- SolidCraft: 0.30.1
- µcad: 0.6.0
- vcad-kernel: 0.11.0 development tree, pinned by Git commit in CI
- CadQuery: 2.8.0
- PythonSCAD: 1.1.2

## Representation note

With the pinned vcad 0.11.0 development kernel, the CSG geometry is correct
(~36,622 mm³) but the second and third cylinder differences currently fall
back from analytic BRep to a watertight mesh. CI treats this as a valid
geometry result while preserving `degradations`, `why_not_brep` and the
stage-by-stage volumes as evidence. The vcad output is therefore STL for this
case unless a later pinned kernel retains BRep and can also emit STEP.

The SCRF script uses plain numeric millimetre values at its call site. The constructor marks `size` with `#[parameter]` under `#[cad]`; the macro preserves named native SolidCraft expressions such as `size / 1.5` without exposing `ParamLength` to the script.
