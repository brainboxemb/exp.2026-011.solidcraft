# Experiment 011 — semantic CAD API, powered by SolidCraft

**Status: active — first Proof of Principle; no live qualification yet.**

Can we describe parts as **CAD objects and features** (box, edges, fillet, holes, workplanes), while an adapter compiles that design into the correct SolidCraft operations? The user's modeling code should not expose `sketch.create`, JSON parameters or transport. **SolidCraft remains the only CAD engine.**

This experiment is isolated from the OpenSCAD model archive and production CAD tooling.

## References

- [SolidCraft](https://github.com/tangency-labs/solidcraft) — the application, CLI, JSON control commands and MCP.
- [scraftpybind](https://github.com/waynegramlich/scraftcnc/tree/main/scraftcnc/pybind) — an **unofficial** Python interface within the broader `scraftcnc` project (we need only the binding, not its CNC components).
- [PartCAD–SolidCraft](https://github.com/partcad/partcad-solidcraft) — a different interoperability mechanism; keep it for a **separate experiment**.

The existing Python binding supports two transports: the GUI's JSON control port and the CLI's headless MCP session. Use the pinned external checkout, not a copy of generated binding code.

**Version caveat:** upstream's Python command classes were generated from SolidCraft CLI **0.20.0**, while the stable release on 9 November 2026 is **0.30.1**. Compatibility must be tested.

## Windows quick start

See [Windows setup](docs/01-windows-setup.md) for installation, including the Chocolatey caveat. In PowerShell from this repository:

```powershell
.\scripts\bootstrap.ps1
$env:PYTHONPATH = (Resolve-Path .\ext\scraftcnc).Path

# Test the upstream Python bindings, from the upstream root:
Push-Location .\ext\scraftcnc
try {
    python -m unittest -v tests.test_scraftpybind
} finally {
    Pop-Location
}

# Requires solidcraft-cli on PATH:
python .\examples\plate.py --target headless --out .\output\plate.step
```

For the GUI, **start SolidCraft normally** and use `--target 0` to discover its default control port (or explicitly start `solidcraft --control 8080` and use `--target 8080`). The example sets the correct Windows token folder automatically; a second PowerShell window still needs `PYTHONPATH`.

Run the independent fixture tests at any time, even without SolidCraft:

```powershell
python -m unittest discover -s tests -v
```

The example is **not yet live-tested** on SolidCraft 0.30.1.

For the simplest alternative, requiring **no Python binding at all**, generate a native JSON script with:

```powershell
python .\\examples\\python_cli_script.py
python .\\examples\\python_cli_script.py --run
```

The first command only writes `output/bracket.json`; the second asks SolidCraft CLI to export `output/bracket.step`.

## Semantic CAD API proof of principle

The [Rust experiment](rust-facade/) now has **two distinct layers**: an engine-independent `cad::Part` domain API and a SolidCraft-specific adapter that turns **one CAD feature into multiple SolidCraft operations**. The current API now supports `.faces(Faces::Top).workplane().circles(&holes)?.cut_through()?`: the adapter creates a **face-attached sketch**, instead of placing a sketch on a floating global XY plane. The earlier 1:1 command facade is retained as a low-level comparison, **not** the target user-facing API. [CadQuery](https://cadquery.readthedocs.io/en/stable/workplane.html) , [vcad](https://docs.rs/vcad/latest/vcad/) and [µcad](https://codeberg.org/microcad/microcad/) are API design references only.

```powershell
cd rust-facade
cargo test
cargo run --bin cad_plate             # semantic CAD API -> SolidCraft script
cargo run --bin cad_plate -- --run    # also ask SolidCraft CLI to export STEP
cargo run --bin solidcraft-facade-poc # previous low-level command wrapper
```

`cad_plate` generates `../output/cad-plate.json`; `--run` additionally invokes the installed `solidcraft-cli` to export `../output/cad-plate.step`. The old `solidcraft-facade-poc` binary generates `rust-bracket.json`. **Offline CI passes:** 8 Rust tests, 8 Python fixture tests, and generated JSON syntax verification. Actual SolidCraft CLI/GUI execution remains **unverified**.

## Windows runtime qualification

After installing official SolidCraft, run this from the repository root:

```powershell
.\scripts\qualify-solidcraft.ps1 -SkipBuild -Snapshot  # direct, no Rust required
.\scripts\qualify-solidcraft.ps1 -Snapshot             # build and test Rust first
```

The [qualification script](scripts/qualify-solidcraft.ps1) finds the installed CLI (normally `C:\Program Files\SolidCraft\solidcraft-cli.exe`), tests the Rust code, builds the semantic CAD script, and asks the actual SolidCraft CLI to export **STEP** and a native **.sc design** with strict parameter checking. Raw measurements/results stay under ignored `output/`. This has **not yet been run against the user's Windows installation**.

See [face selection/workplane notes](docs/08-face-workplanes.md).

## Qualification

- **PY-01** — offline Python transport tests and pinned bootstrap.
- **PY-02** — Windows GUI commands build a visible plate.
- **PY-03** — headless MCP builds the same plate and exports STEP.
- **PY-04** — save/reopen a native design and change a named parameter.
- **PY-05** — document version and error compatibility, then decide whether a small adapter is needed.

See [plan](docs/00-plan.md), [semantic CAD API and CadQuery ideas](docs/05-cad-api-design.md), [face workplanes](docs/08-face-workplanes.md), [µcad API inspiration](docs/07-microcad-inspiration.md), [offline verification](docs/06-verification.md), [low-level Rust command facade](docs/04-rust-command-facade.md), [scripting options](docs/03-scripting-options.md), [first findings](docs/02-first-findings.md) and [tracking issue #1](https://github.com/brainboxemb/exp.2026-011.solidcraft/issues/1).

## Docker and production boundary

No new Docker repository now. If container reproducibility becomes a concrete requirement, start with a Dockerfile **inside this experiment**. PartCAD integration remains separate, and no production library/migration is authorized by the initial PoP.

Shared rules: [brainboxemb.meta](https://github.com/brainboxemb/brainboxemb.meta).
