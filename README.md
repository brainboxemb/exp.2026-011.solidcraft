# Experiment 011 — SolidCraft Python interface

**Status: active — first Proof of Principle; no live qualification yet.**

Can we build and modify parametric SolidCraft models using Python, both in its Windows GUI and headless, without creating another CAD protocol client?

This experiment is isolated from the OpenSCAD model archive and production CAD tooling.

## References

- [SolidCraft](https://github.com/tangency-labs/solidcraft) — the application, CLI, JSON control commands and MCP.
- [scraftpybind](https://github.com/waynegramlich/scraftcnc/tree/main/scraftcnc/pybind) — an **unofficial** Python interface within the broader `scraftcnc` project (we need only the binding, not its CNC components).
- [PartCAD–SolidCraft](https://github.com/partcad/partcad-solidcraft) — a different interoperability mechanism; keep it for a **separate experiment**.

The Python binding supports two transports: the GUI's JSON control port and the CLI's headless MCP session. Use the pinned external checkout, not a copy of generated binding code.

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

## Qualification

- **PY-01** — offline Python transport tests and pinned bootstrap.
- **PY-02** — Windows GUI commands build a visible plate.
- **PY-03** — headless MCP builds the same plate and exports STEP.
- **PY-04** — save/reopen a native design and change a named parameter.
- **PY-05** — document version and error compatibility, then decide whether a small adapter is needed.

See [plan](docs/00-plan.md), [scripting alternatives](docs/03-scripting-options.md), [first findings](docs/02-first-findings.md) and [tracking issue #1](https://github.com/brainboxemb/exp.2026-011.solidcraft/issues/1).

## Docker and production boundary

No new Docker repository now. If container reproducibility becomes a concrete requirement, start with a Dockerfile **inside this experiment**. PartCAD integration remains separate, and no production library/migration is authorized by the initial PoP.

Shared rules: [brainboxemb.meta](https://github.com/brainboxemb/brainboxemb.meta).
