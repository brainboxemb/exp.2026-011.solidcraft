# CSG cube API comparison

This example is deliberately small: one parameter, primitive solids and boolean
operations. It is intended to compare **modeling syntax**, not geometry engines.

All variants describe the same intent:

1. intersect a sphere with a cube;
2. create three orthogonal cylinders;
3. subtract the cylinders from the body;
4. use a nominal size of 50 mm.

## Variants

- `ours/model.rs` — Experiment 011's actual Rust CAD scripting style. A named
  `part!(...)` defines a reusable CAD part and `root!(...)` selects the
  top-level instance. There is no CLI, JSON, transport or SolidCraft setup in
  the model file.
- `ours/solidcraft.json` — the reviewed raw SolidCraft command sequence
  generated from our Rust model. This stays beside the model so command quality
  can be inspected as well as final geometry.
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

## Why `part!` and `root!`?

The model should have a named, reusable top-level CAD concept rather than being
an anonymous Rust block. `part!` gives the model a name and typed parameters.
Plain Rust cannot execute `CsgCube(50.mm())` directly at module scope, so the
small `root!` macro marks the top-level instance without introducing a
`main()` function into the CAD source.

## Tested versions

- Experiment 011: current branch implementation
- SolidCraft: 0.30.1
- µcad: 0.6.0
- vcad-kernel: 0.11.0 development tree, pinned by Git commit in CI
- CadQuery: 2.8.0
- PythonSCAD: 1.1.2
