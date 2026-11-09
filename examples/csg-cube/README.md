# CSG cube API comparison

This example is deliberately small: one parameter, primitive solids and boolean
operations. It is intended to compare **modeling syntax**, not geometry engines.

All variants describe the same intent:

1. intersect a sphere with a cube;
2. create three orthogonal cylinders;
3. subtract the cylinders from the body;
4. use a nominal size of 50 mm.

## Variants

- `ours/model.rs` — target style for Experiment 011: Rust CAD model code without CLI/transport boilerplate.
- `ours/solidcraft.json` — the raw SolidCraft command sequence the implementation should compile the model to. Keep this beside the model so command quality can be reviewed.
- `microcad/model.µcad` — µcad reference implementation.
- `vcad/model.rs` — vcad Rust-kernel reference implementation.
- `cadquery/model.py` — CadQuery reference implementation.

The reference implementations are design comparisons only. Experiment 011 still
uses SolidCraft as its geometry engine.

> Note: `ours/model.rs` is a **target API example**. The current Rust facade
> does not yet implement all primitives, boolean operators, `part!`, or the
> no-boilerplate runner needed to compile this file directly.
