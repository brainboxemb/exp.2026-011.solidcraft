# Rust proof of principle — semantic CAD API for SolidCraft

The experimental crate has **three layers**:

| Layer | Location | Responsibility |
|---|---|---|
| **CAD domain** | [`src/cad.rs`](src/cad.rs) | `Part`, `Hole`, `Edges`, `fillet`, `through_holes`; no JSON or SolidCraft terms in the public modeling calls |
| **SolidCraft adapter** | [`src/solidcraft_adapter.rs`](src/solidcraft_adapter.rs) | Turns one semantic feature into the required sequence of SolidCraft sketches, extrusion/cut and fillet |
| **Command/transport** | [`src/lib.rs`](src/lib.rs) | Native command objects, `CommandTransport`, `ScriptTransport`; later GUI and MCP |

`vcad` and `CadQuery` are **API design references**, not dependencies
and not alternative modeling engines. No geometry kernel is implemented here.

## Readable model code

The actual example is [`src/bin/cad_plate.rs`](src/bin/cad_plate.rs):

```rust
let plate = Part::box3d(100.0, 60.0, 10.0)?
    .named("Plate")
    .edges(Edges::OuterVertical).fillet(2.0)?
    .through_holes(&holes)?;

let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
cad.build(&plate)?;
```

**Only the adapter knows about SolidCraft command IDs.** This is not a
one-function-per-SolidCraft-command wrapper. One `Part::box3d` emits
sketch-create, rectangle, finish and extrude; one `through_holes`
emits a top-face sketch, N circles, sketch-finish and a cut.

## Running

From the repository root:

```powershell
cargo test --manifest-path rust-facade/Cargo.toml
cargo run --manifest-path rust-facade/Cargo.toml --bin cad_plate
cargo run --manifest-path rust-facade/Cargo.toml --bin cad_plate -- --run
```

First command tests CAD semantics and translation without SolidCraft.
Second generates ignored `output/cad-plate.json` without installing
SolidCraft. Third also invokes `solidcraft-cli` to request a STEP export;
it requires a current SolidCraft installation.

The **older command wrapper** remains as a separate comparison binary:

```powershell
cargo run --manifest-path rust-facade/Cargo.toml --bin solidcraft-facade-poc
```

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
- No named workplanes or topological tags yet; investigate the approach
  from CadQuery in [design notes](../docs/05-cad-api-design.md).
- `ScriptTransport` cannot return generated curve/feature IDs. Dynamic
  selections and better parametric updating need a live GUI/MCP backend.
- A generated STEP model is not evidence of editable SolidCraft native
  feature history. Native save/reopen qualification is separate.
- **No Rust compiler or SolidCraft runtime has yet been executed in
  the connected authoring environment.** Source changes are not
  proof of actual CAD results.

See [the experiment plan](../docs/00-plan.md) for qualification cases.
