# Experiment 011 — SCPF (Python interface to SolidCraft)

**Current direction: Python SCPF.** The Rust variant is **SCRF** (SolidCraft Rust Forge). The earlier Rust SCRF
prototype remains in this repository as a preserved reference, not as the
intended user-facing scripting language.

SCPF aims to make CAD scripts easier to read and more expressive than
OpenSCAD while delegating **all geometry** to the existing SolidCraft engine.
SolidCraft's own MCP and RPC controls already exist and are outside SCPF's scope.

Start with the [SCPF guide](scpf/README.md) and its two minimal scripts:
[Plate](examples/plate/scpf/model.py) and
[CsgCube](examples/csg-cube/scpf/model.py).

```python
@dataclass
class Plate:
    length: float = 100
    width: float = 60
    thickness: float = 10

    def build(self):
        body = Box(self.length, self.width, self.thickness).fillet(2)
        holes = Cylinder(self.thickness, 8).pattern(x=70, y=30)
        body - holes

Plate()
```

Model scripts need no import statements, `main()`, `show()` or explicit
`return`. The injected `@dataclass` decorator declares reusable Python CAD
objects. SCPF invokes `build()` automatically and derives named parameters
from the object's fields before generating native SolidCraft command JSON.

Run the independent SCPF tests with `PYTHONPATH=scpf`:

```powershell
$env:PYTHONPATH = "scpf"
python -m unittest discover -s scpf/tests -v
python -m scpf examples/plate/scpf/model.py --out output/examples/plate/scpf/solidcraft.json
```

The SCPF CI workflow retains generated JSON as GitHub Actions artifacts.
The integrated `bld` workflow retains both Rust and Python output JSON
only after successful checks; `vrf` retains native geometry evidence.
The separate `generated-examples` orphan branch remains reserved for
qualified comparisons.

---

# Archived Rust prototype — SCRF (SolidCraft Rust Forge)


**Status: active Rust proof of principle; the first native SolidCraft 0.30.1 fixture now executes successfully.**

The goal is a readable **CAD interface** in Rust: model code describes parts, holes, faces, workplanes and fillets. A SolidCraft adapter translates that intent into native SolidCraft operations. **SolidCraft remains the only geometry engine.**

The comparison covers **five implementations**: SCRF, CadQuery, vcad, µcad and PythonSCAD. The other four are API-design references, not SCRF geometry backends.

The user-facing scripts contain no `main()`, runner calls or output plumbing.
They define ordinary Rust object types and end with the object expression to build.

## Architecture

```text
SCRF script
  ordinary Rust objects + final model expression
                 ↓
SCRF domain / adapter
                 ↓
native SolidCraft operations
                 ↓
SolidCraft
  geometry + native feature history
```

## Example

The user-facing Plate script is
[`examples/plate/scrf/model.rs`](examples/plate/scrf/model.rs):

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

The `#[cad]` macro processes `#[parameter]` arguments into editable SolidCraft dimensions. There is no `use`, `Result`, `?`, `main()`, `show()`, `build!()` or transport code in that file. Common CAD types are implicitly imported by the runner.

The Cargo examples under `scrf/examples/` are only test harnesses
that compile these expression-based scripts and compare the generated native
SolidCraft command plan.

## Example

The executable Cargo harness is `scrf/examples/plate.rs`; it is not part of the script syntax.

```powershell
cargo run --manifest-path scrf/Cargo.toml --example plate
```

It compiles the script and writes `output/examples/plate/scrf/solidcraft.json`.

## Rust tests


```powershell
cargo test --manifest-path scrf/Cargo.toml --all-targets
cargo run --manifest-path scrf/Cargo.toml --example plate
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

The offline build publishes generated command JSON to `bld` after success; native qualification publishes its SolidCraft outputs (including command JSON, STEP, `.sc` and measurements) to `vrf` after success. Both branches are CI-owned, and their existence is contingent on a successful run.

Comparison workflows produce CAD exports and measurements for both
`plate` and `csg-cube`. The agreed publication target is an **orphan
`generated-examples` branch** containing all five implementations for both
examples, with a GitHub Pages overview. It is not created until all five
results qualify; current outputs remain GitHub Actions artifacts.

Before publication, collect the results under
`output/staging/{plate,csg-cube}/{scrf,cadquery,microcad,vcad,pythonscad}/`
and run:

```powershell
python scripts/check-generated-examples.py output/staging
```

This automated gate checks expected cases, basic volume ranges, non-empty
CAD exports and diagnostics for vcad's mesh fallback. It is **not** a
substitute for the full CI checks or visual inspection.
See [the experiment plan](docs/00-plan.md#generated-model-evidence).

The generated SCRF command JSON is retained on the `bld` orphan
branch after successful offline CI; native SolidCraft verification outputs are
retained on `vrf` after successful native CI. The future
`generated-examples` branch will hold all five comparison variants together.
