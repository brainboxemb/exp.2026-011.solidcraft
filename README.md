# Experiment 011 — SolidCraftForge

**Status: active Rust proof of principle; the first native SolidCraft 0.30.1 fixture now executes successfully.**

The goal is a readable **CAD interface** in Rust: model code describes parts, holes, faces, workplanes and fillets. A SolidCraft adapter translates that intent into native SolidCraft operations. **SolidCraft remains the only geometry engine.**

The comparison covers **five implementations**: SolidCraftForge, CadQuery, vcad, µcad and PythonSCAD. The other four are API-design references, not SolidCraftForge geometry backends.

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
    pub fn new(length: f64, width: f64, thickness: f64) -> Shape {
        let cylinders = Cylinder::new(thickness, 8.0)
            .rectangular_pattern(70.0, 30.0);

        Shape::box3d(length, width, thickness)
            .named("Plate")
            .fillet(Edges::OuterVertical, 2.0)
            .subtract(cylinders)
    }
}

Plate::new(100.0, 60.0, 10.0)
```

There is no `use`, `Result`, `?`, `main()`, `show()`, `build!()` or transport code in that file. Common CAD types are implicitly imported by the runner.

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

## Generated comparison results

Comparison workflows produce CAD exports and measurements for both
`plate` and `csg-cube`. The agreed publication target is an **orphan
`generated-examples` branch** containing all five implementations for both
examples, with a GitHub Pages overview. It is not created until all five
results qualify; current outputs remain GitHub Actions artifacts.

Before publication, collect the results under
`output/staging/{plate,csg-cube}/{solidcraftforge,cadquery,microcad,vcad,pythonscad}/`
and run:

```powershell
python scripts/check-generated-examples.py output/staging
```

This automated gate checks expected cases, basic volume ranges, non-empty
CAD exports and diagnostics for vcad's mesh fallback. It is **not** a
substitute for the full CI checks or visual inspection.
See [the experiment plan](docs/00-plan.md#generated-model-evidence).

The generated SolidCraftForge command JSON is retained on the `bld` orphan
branch after successful offline CI; native SolidCraft verification outputs are
retained on `vrf` after successful native CI. The future
`generated-examples` branch will hold all five comparison variants together.
