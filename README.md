# Experiment 011 — SolidCraftForge

**Status: active Rust proof of principle; the first native SolidCraft 0.30.1 fixture now executes successfully.**

The goal is a readable **CAD interface** in Rust: model code describes parts, holes, faces, workplanes and fillets. A SolidCraft adapter translates that intent into native SolidCraft operations. **SolidCraft remains the only geometry engine.**

CadQuery, vcad, µcad and PythonSCAD are references for API design only.

The user-facing scripts contain no `main()`, runner calls or output plumbing.
They define ordinary Rust object types and end with the object expression to build.

## Architecture

```text
SolidCraftForge script
  ordinary Rust objects + final model expression
                 ↓
SolidCraftForge domain / adapter
                 ↓
native SolidCraft operations
                 ↓
SolidCraft
  geometry + native feature history
```

## Example

The user-facing Plate script is
[`examples/plate/solidcraftforge/model.rs`](examples/plate/solidcraftforge/model.rs):

```rust
pub struct Plate;

impl Plate {
    pub fn new(length: Length, width: Length, thickness: Length) -> Result<Part, DesignError> {
        // build the semantic Plate object
    }
}

Plate::new(100.mm(), 60.mm(), 10.mm())?
```

There is no `main()`, `show()`, `build!()` or transport code in that file.

The Cargo examples under `solidcraftforge/examples/` are only test harnesses
that compile these expression-based scripts and compare the generated native
SolidCraft command plan.

## Example

The executable Cargo harness is `solidcraftforge/examples/plate.rs`; it is not part of the script syntax.

```powershell
cargo run --manifest-path solidcraftforge/Cargo.toml --example plate
```

It compiles the script and writes `output/examples/plate/solidcraftforge/solidcraft.json`.

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
