# Bracket — SCPF live CAD example

This small L bracket demonstrates a parameterized XZ sketch, extrusion,
fillet and two mounting holes, using SolidCraft's native CAD command API.

- [Python design](scpf/model.py): reusable `Bracket` dataclass, `build()`, no explicit `return` or `show()`.
- [SCPF command fixture](scpf/solidcraft.json): standalone command sequence.
- [Original SolidCraft commands](source/bracket.json): supplied reference; works with parameters already declared.
- [SCPF runner instructions](../../scpf/README.md#run-and-inspect-the-bracket): PowerShell examples for `--out`, `--connect`, and the CLI.
- [Results website](../../site/): generated automatically by GitHub Actions.

## Why the two JSON files start differently

The original reference starts with `parameters.change`: it expects
`width` and `thickness` to exist in the current document. SCPF uses
`parameters.add` to create them in an empty design. Beyond those first
two commands, the geometry operations must agree.

The XZ sketch's positive vertical coordinate maps to **negative world Z**.
The valid fillet point is `[40, -30, -6]` and the through-hole cut also
travels along negative Z.

## Run on Windows

From the repository root:

```powershell
$env:PYTHONPATH = "scpf"
python -m scpf examples/bracket/scpf/model.py --out output/examples/bracket/scpf/solidcraft.json
code output/examples/bracket/scpf/solidcraft.json
```

To replay the **original command JSON without translating it**:

```powershell
python -m scpf replay examples/bracket/source/bracket.json
```

The original file starts with `parameters.change`, so `width` and
`thickness` must already exist in the current design. In a new empty
design, replay the standalone SCPF file instead:

```powershell
python -m scpf replay examples/bracket/scpf/solidcraft.json
```

To send commands to an **already open SolidCraft** instance, first open a
new empty design and enable external Assistant control:

```powershell
python -m scpf examples/bracket/scpf/model.py --connect
```

A live batch does not write a file. The existing design may be modified.
If the build fails, the control request asks SolidCraft to roll back.

For native CLI evaluation without a GUI connection:

```powershell
solidcraft-cli run output/examples/bracket/scpf/solidcraft.json --param-check strict --save output/bracket.sc
```

Open `output/bracket.sc` in SolidCraft. Native execution of this particular
Bracket model must be verified independently from Python command-generation
tests.
