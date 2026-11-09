# SolidCraftForge

The experimental crate has **three layers**, but only one public modeling direction:

| Layer | Location | Responsibility |
|---|---|---|
| **CAD domain** | [`src/cad.rs`](src/cad.rs) | `Part`, `Hole`, `Edges`, `fillet`, `through_holes`; no JSON or SolidCraft terms in the public modeling calls |
| **SolidCraft adapter** | [`src/solidcraft_adapter.rs`](src/solidcraft_adapter.rs) | Turns one semantic feature into the required sequence of SolidCraft sketches, extrusion/cut and fillet |
| **Command/transport** | [`src/lib.rs`](src/lib.rs) | Native command objects, `CommandTransport`, `ScriptTransport`; later GUI and MCP |

`vcad`, `CadQuery` and `µcad` are **API design references**, not dependencies
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

## Running

From the repository root:

```powershell
cargo test --manifest-path solidcraftforge/Cargo.toml
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate -- --run
```

First command tests CAD semantics and translation without SolidCraft.
Second generates ignored `output/cad-plate.json` without installing
SolidCraft. Third also invokes `solidcraft-cli` to request a STEP export;
it requires a current SolidCraft installation.

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
