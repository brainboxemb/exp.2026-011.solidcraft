# 04 — vcad: a Rust-first CAD alternative (source review)

**Status: research note, not yet an implementation experiment.**

User-provided reference: [`vcad` crate API](https://docs.rs/vcad/latest/vcad/).
Upstream source currently resolves to
[`muni-works/vcad`](https://github.com/muni-works/vcad).
This is **not** the same application as SolidCraft.

## Why this changes the scripting comparison

With SolidCraft, we are currently scripting a *separate running CAD application*
through its command interface. In Python, the first proof of principle can
simply use `subprocess` to run a JSON file. Rust could do the same, but it is
not inherently better merely because SolidCraft is written in Rust.

With `vcad`, Rust itself becomes the modeling language:
`Part::cube`, `Part::cylinder`, `difference`, `translate`, and export
are ordinary library calls. There is no need to build a Python wrapper or
start SolidCraft just to construct and export geometry.

The [published `vcad` 0.10.0 documentation](https://docs.rs/vcad/0.10.0/vcad/)
gives this example:

```rust
use vcad::{centered_cube, Part};

let cube = centered_cube("block", 20.0, 10.0, 5.0);
let hole = Part::cylinder("hole", 3.0, 10.0, 32)
    .translate(0.0, 0.0, -2.5);
let result = cube.difference(&hole);
result.write_stl("block_with_hole.stl").unwrap();
```

This API resembles the *code-first CSG* style of our OpenSCAD archive much
more than SolidCraft's sequence of sketches and timeline features.

## Version and geometry caveat

The current docs.rs release (at this investigation, 9 November 2026) is
`vcad` **0.10.0**. The crate documentation identifies `vcad::Part` as a
**legacy manifold / mesh-CSG API**, maintained as an ergonomic Rust interface
while migration to the newer `vcad-kernel` BRep kernel is planned.
See [issue #10](https://github.com/muni-works/vcad/issues/10).

Thus do not infer that every boolean or export from `vcad::Part` uses the
new BRep kernel. The newer project exposes `vcad_kernel::Solid`, but the
library APIs and exact behavior need separate evaluation.

`Part` can retain its operation tree as an IR document, but that does not
equate to a SolidCraft native `.sc` feature timeline. STEP interchange is
not a round-trip of editable source history between these different systems.

## Useful comparison

| Requirement | SolidCraft + Python | `vcad` + Rust |
|---|---|---|
| Write a small code-first CAD model | Commands assembled in Python | Direct model API in Rust |
| GUI feedback while modeling | SolidCraft control port / MCP bridge | Separate vcad app/preview workflow; must verify exact integration |
| Learn the geometry API | SolidCraft command registry and timeline | `Part` methods or newer `vcad-kernel` |
| Build/run iteration | Python script plus installed CLI | Rust `cargo run` plus Rust dependencies |
| Code-first CSG model | Possible, but feature commands drive it | Natural fit for `Part` booleans |
| Edit feature history in SolidCraft | Native SolidCraft model | Not automatically preserved on import |
| Stable engine boundary | CLI/JSON command contract | Pinned crate API; review evolving kernel |

## Recommended next experiment decision

1. Continue **Experiment 011** with SolidCraft in the Windows GUI and Python,
   because we want to understand and control that application.
2. As a separate *candidate comparison*, create the **same test bracket**
   in a tiny pinned Rust `vcad` Cargo project, exporting STL/STEP and
   checking dimensions, hole geometry and build times.
3. Do not create or number an additional experiment repository automatically.
   First decide whether this is a one-off comparative fixture or deserves
   independent scope.
4. Keep **Experiment 012** for PartCAD's SolidCraft adapter; `vcad` is
   not PartCAD.

No code has been compiled or exported in the `vcad` path in this note.
