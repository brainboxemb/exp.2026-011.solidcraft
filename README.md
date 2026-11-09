# Experiment 011 — SolidCraftForge — Rust modeling and automation for SolidCraft

**Status: active Rust proof of principle; the first native SolidCraft 0.30.1 fixture now executes successfully.**

The goal is a readable **CAD interface** in Rust: model code describes parts, holes, faces, workplanes and fillets. A SolidCraft adapter translates that intent into native SolidCraft operations. **SolidCraft remains the only geometry engine.**

CadQuery, vcad, µcad and PythonSCAD are references for API design only.

The user-facing scripts contain no `main()`, runner calls or output plumbing.
They define ordinary Rust object types and end with the object expression to build.

## Architecture

```text
Rust CAD domain
  Part / Hole / Face / Workplane / Fillet
                 ↓
SolidCraft adapter
  CAD feature → one or more native operations
                 ↓
Transport
  JSON script now; GUI / MCP later
                 ↓
SolidCraft
  geometry + native feature history
```

Example:

```rust
let plate = Part::box3d(100.0, 60.0, 10.0)?
    .named("Plate")
    .edges(Edges::OuterVertical).fillet(2.0)?
    .faces(Faces::Top).workplane()
    .circles(&holes)?
    .cut_through()?;

let mut solidcraft = SolidCraftAdapter::new(ScriptTransport::default());
solidcraft.build(&plate)?;
```

## Example

The complete user-facing example is [`solidcraftforge/examples/plate.rs`](solidcraftforge/examples/plate.rs).

```powershell
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate
```

It creates the plate through the semantic CAD API and writes `output/cad-plate.json`.

## Rust tests


```powershell
cargo test --manifest-path solidcraftforge/Cargo.toml --all-targets
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate
```

## Test against SolidCraft on Windows

No Rust installation is required with the committed fixture:

```powershell
.\scripts\qualify-solidcraft.ps1 -SkipBuild -Snapshot
```

Or compile the Rust model first:

```powershell
.\scripts\qualify-solidcraft.ps1 -Snapshot
```

See [plan](docs/00-plan.md), [Windows setup](docs/01-windows-setup.md), [CAD API design](docs/05-cad-api-design.md), [verification](docs/06-verification.md), [µcad inspiration](docs/07-microcad-inspiration.md), and [face/workplane design](docs/08-face-workplanes.md).
