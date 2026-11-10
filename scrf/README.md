# SCRF — SolidCraft Rust Forge

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

The user-facing examples live under `examples/*/scrf/model.rs`.
They are scripts rather than Cargo programs: no `main()`, no `show()`, no
`build!()`. A reusable Rust type is defined and the final expression creates
the model, for example:

```rust
pub struct CsgCube;

#[cad]
impl CsgCube {
    pub fn new(#[parameter] size: f64) -> Shape {
        let body = Sphere::new(size / 1.5) & Cube::new(size);
        let holes = Cylinder::new(size, size / 1.5).orient([X, Y, Z]);
        body - holes
    }
}

CsgCube::new(50.0)
```

The Plate model uses ordinary numbers in millimetres, creates a set of
cylindrical cutters, and subtracts them from the solid. The error-aware
builder is internal to SCRF:

```rust
pub struct Plate;

#[cad]
impl Plate {
    pub fn new(
        #[parameter] length: f64,
        #[parameter] width: f64,
        #[parameter] thickness: f64,
    ) -> Shape {
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

The external runner automatically imports common SCRF types.
No `use`, `Result`, `?`, `main`, or output plumbing is required in the
model file. The adapter still preserves SolidCraft's native sketch/history.

The Cargo files under `scrf/examples/` are test harnesses only.
They are not part of the model syntax.

All plain numbers are millimetres. For box dimensions, the adapter creates
editable SolidCraft parameters (`length`, `width`, `thickness`) internally.
The CSG cube's annotated `size` becomes a symbolic SolidCraft parameter.
Expressions like `size / 1.5` remain symbolic in the generated command plan.
This works for the supported f64 parameter annotations and CSG operations;
arbitrary Rust expressions and parameter types are not automatically supported.

Both feature-based CAD and CSG scripts return the same public `Shape`.
The runner translates it into the appropriate internal Part or CSG
representation. Users do not need to distinguish those implementations.

## Running

From the repository root:

```powershell
cargo test --manifest-path scrf/Cargo.toml
cargo run --manifest-path scrf/Cargo.toml --example plate
```

First command tests CAD semantics and translation without SolidCraft.
Second compiles the expression-based Plate script and generates ignored `output/examples/plate/scrf/solidcraft.json`. Native SolidCraft execution is qualified separately by CI and `scripts/qualify-solidcraft.ps1`.

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

## Rust prototype naming

The Rust crate is named **`scrf`** (SolidCraft Rust Forge). Legacy source and JSON fixture directories retain their `scrf/` paths so the completed PR #2 evidence, CI commands, and historical links remain reproducible. **SCPF** is the separate, primary Python experiment.

## Build and verification results

A successful offline SCRF workflow publishes its generated JSON
command plans to an orphan `bld` branch (and retains an Actions artifact).
Successful native SolidCraft qualification publishes STEP, native `.sc`,
previews when available, and verification JSON to an orphan `vrf` branch.
Both branches are workflow outputs, not source branches; they are created
only when the corresponding GitHub Actions job succeeds. No branch creation
is implied by a local compilation.

The agreed `generated-examples` orphan branch remains a **separate**
publication gate: it will contain **all five** implementations together,
only after their comparative geometry is checked.
