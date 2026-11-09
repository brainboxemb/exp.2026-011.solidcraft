# Rust proof of principle — semantic CAD API for SolidCraft

The experimental crate has **three layers**:

| Layer | Location | Responsibility |
|---|---|---|
| **CAD domain** | [`src/cad.rs`](src/cad.rs) | `Part`, `Hole`, `Edges`, `fillet`, `through_holes`; no JSON or SolidCraft terms in the public modeling calls |
| **SolidCraft adapter** | [`src/solidcraft_adapter.rs`](src/solidcraft_adapter.rs) | Turns one semantic feature into the required sequence of SolidCraft sketches, extrusion/cut and fillet |
| **Command/transport** | [`src/lib.rs`](src/lib.rs) | Native command objects, `CommandTransport`, `ScriptTransport`; later GUI and MCP |

`vcad`, `CadQuery` and `µcad` are **API design references**, not dependencies
and not alternative modeling engines. No geometry kernel is implemented here.

## Readable model code

The actual example is [`src/bin/cad_plate.rs`](src/bin/cad_plate.rs):

```rust
let plate = Part::box3d(
    LengthParam::new("plate_length", Length::mm(100.0))?,
    LengthParam::new("plate_width", Length::mm(60.0))?,
    LengthParam::new("thickness", Length::mm(10.0))?,
)?
    .named("Plate")
    .edges(Edges::OuterVertical).fillet(2.0)?
    .faces(Faces::Top).workplane().circles(&holes)?.cut_through()?;

let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
cad.build(&plate)?;
```

The box dimensions above are **CAD-domain parameters**. The adapter emits the native parameter definitions and uses their expressions in the sketch/extrusions; the user does not call `parameters.change`.

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
- A limited `.faces(Faces::Top).workplane()` is now implemented, attached to a real SolidCraft source face; arbitrary faces, local-coordinate transforms and stable general topology references are **not** yet supported. See [workplane notes](../docs/08-face-workplanes.md).
- `ScriptTransport` cannot return generated curve/feature IDs. Dynamic
  selections and better parametric updating need a live GUI/MCP backend.
- A generated STEP model is not evidence of editable SolidCraft native
  feature history. Native save/reopen qualification is separate.
- **Offline CI verifies the Rust CAD API and command fixture, not actual CAD geometry.**
  The SolidCraft runtime, STEP output and GUI/MCP integration are unqualified.

See [the experiment plan](../docs/00-plan.md) for qualification cases.
