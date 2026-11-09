# 00 — Experiment plan

## Problem

We want a readable Python interface for SolidCraft that can:
- drive models in the interactive GUI, where we can watch each operation;
- run the same design headless for reproducible automated checks;
- create and modify parametric designs rather than only export static solids.

## Existing mechanism to evaluate

`waynegramlich/scraftcnc` contains `scraftcnc/pybind/scraftpybind.py`, an unofficial Python binding generated from SolidCraft commands.

It provides:
- `ControlTransport` — a JSON control port in a running GUI;
- `HeadlessTransport` — the CLI's headless MCP mode;
- `PyBind` — Python methods matching SolidCraft command namespaces;
- `scraftpybind_generate.py` — code generation from SolidCraft command metadata.

First compare the **simpler Python-generated JSON script** against the existing Python binding; the script requires no bindings and is a useful baseline. Do not copy generated bindings prematurely. Pin upstream, execute examples, and identify version or Python-API gaps.

Upstream baseline when this experiment was opened:
`waynegramlich/scraftcnc@eef7b7c96e2c829f82271827c7c16fb7ad95668b` (8 November 2026).
The upstream generator's cached command contract is SolidCraft 0.20.0; first target stable runtime is 0.30.1 (2 November 2026). Both are **observed versions**, not a compatibility claim.

## Qualification cases

| Case | What to demonstrate | Evidence to retain |
|---|---|---|
| PY-01 | Python dependency bootstrap and offline tests | command, interpreter and test output |
| PY-02 | GUI JSON-control modeling on Windows | commands, SolidCraft version and screenshot |
| PY-03 | Headless MCP modeling and STEP export | script output and exported STEP |
| PY-04 | Native design parameter change and reopen | initial/final values, saved native design |
| PY-05 | Version compatibility and error behavior | exact version, expected and actual behavior |

## Decisions

- Start with Python and native Windows execution.
- Only introduce a local Dockerfile for a concrete reproducibility need.
- Keep PartCAD exploration in a different experiment, proposed `exp.2026-012.partcad-solidcraft`.
- Never substitute STEP geometry for proof that a SolidCraft *design history* remains editable.
- Preserve third-party licensing and provenance; no vendor copy is needed for the initial experiment.

## Explicitly out of scope

- CNC toolpaths or running G-code from `scraftcnc`;
- general-purpose SolidCraft framework/tooling released to other projects;
- migration of OpenSCAD models;
- a shared `docker.cad-toolchain` repository.
