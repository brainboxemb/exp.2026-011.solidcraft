# SolidCraftForge

The experimental crate has **four technical layers**, but only one public modeling direction:

| Layer | Location | Responsibility |
|---|---|---|
| **CAD domain** | [`src/cad.rs`](src/cad.rs) | `Part`, `Hole`, `Edges`, `fillet`, `through_holes`; no JSON or SolidCraft terms in public modeling calls |
| **CSG domain** | [`src/csg.rs`](src/csg.rs) | primitive solids and boolean expressions |
| **Script boundary** | [`src/script.rs`](src/script.rs) | technical conversion of a script's final Rust object into one common runner model |
| **SolidCraft adapter / transport** | [`src/solidcraft_adapter.rs`](src/solidcraft_adapter.rs), [`src/lib.rs`](src/lib.rs) | translate the model to native SolidCraft operations and carry those operations to SolidCraft |

`vcad`, `CadQuery`, `µcad` and PythonSCAD are **API design references**, not dependencies
and not alternative modeling engines. No geometry kernel is implemented here.

## Readable model code

The user-facing examples live under `examples/*/solidcraftforge/model.rs`.
They are scripts rather than Cargo programs: no `main()`, no `show()`, no
`build!()`. A reusable Rust type is defined and the final expression creates
the model, for example:

```rust
pub struct CsgCube;

impl CsgCube {
    pub fn new(size: Length) -> Shape {
        // construct the CAD object
    }
}

CsgCube::new(50.mm())
```

The Cargo files under `solidcraftforge/examples/` are test harnesses only.
They are not part of the model syntax.

Ordinary `Length` arguments passed to `Part::box3d()` automatically become\neditable SolidCraft dimensions (`length`, `width`, `thickness`). The script\ndoes not construct `LengthParam` objects. Explicit `LengthParam` is retained\nfor advanced domain callers; plain numeric shorthand remains fixed.\n\nThe build-time wrapper also no longer needs to know whether a model returns
`Shape` or `Part`. Both are converted outside the user script through
`IntoScriptModel`. This keeps the special-case runner plumbing out of
`model.rs`.

## Running

From the repository root:

```powershell
cargo test --manifest-path solidcraftforge/Cargo.toml
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate
```

First command tests CAD semantics and translation without SolidCraft.
Second compiles the expression-based Plate script and generates ignored `output/examples/plate/solidcraftforge/solidcraft.json`. Native SolidCraft execution is qualified separately by CI and `scripts/qualify-solidcraft.ps1`.

## Explicit limitations

- The domain supports only an axis-aligned base box (XY centered, z=0..H),
  outside vertical edge fillets on that base, and circular through-holes
  along global Z. It does not compute topology or BRep itself.
- `Edges::OuterVertical` is deliberately **not** an all-purpose selector:
  the adapter currently knows the four original box corners and picks
  their edges at z=H/2. This must be checked against SolidCraft's live
  geometry API before further selectors are added.
- Features are applied in the caller's order. The example fillets the
  outer upright edges **before** drilling holes.
- A limited `.faces(Faces::Top).workplane()` is now implemented, attached to a real SolidCraft source face; arbitrary faces, local-coordinate transforms and stable general topology references are **not** yet supported. See [workplane notes](../docs/08-face-workplanes.md).
- `ScriptTransport` cannot return generated curve/feature IDs. Dynamic
  selections and better parametric updating need a live GUI/MCP backend.
- Basic native save/reopen and parameter-driven rebuild are now qualified for
  the plate fixture. This does not yet establish robust editing for arbitrary
  topology or feature combinations.
- Offline CI verifies the Rust API and command fixture; a separate pinned
  SolidCraft 0.30.1 runtime workflow verifies the plate geometry and basic
  parametric rebuild. GUI/MCP transports remain unqualified.

See [the experiment plan](../docs/00-plan.md) for qualification cases.
