# 00 — Experiment plan

## Problem

We want a **semantic CAD API**, with a typed Rust proof of principle (Python still a useful reference), that can:
- describe geometry and modifications as CAD concepts (Part, Hole, EdgeSelector, Fillet) **without SolidCraft-specific commands**;
- map each high-level feature to one or many SolidCraft operations in an adapter;
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

Compare the **simpler Python-generated JSON script** and existing Python bindings against a **semantic Rust CAD API** whose SolidCraft adapter generates the right sequence of native commands. `vcad`, **CadQuery**, and **µcad** are inspirations for public API ergonomics only; we are not evaluating or integrating their engines. The JSON script is a transport baseline, not the desired final abstraction. Do not copy generated bindings prematurely. Pin upstream, execute examples, and identify version or Python-API gaps.

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
| API-01 | Compact Rust facade produces the expected SolidCraft command IDs and parameters | offline Rust tests and generated JSON |
| API-02 | The same semantic model can switch from script transport to a live transport without rewriting CAD calls | identical model logic, command/result evidence |
| API-03 | Domain-level `Part`, `Hole`, `Edges`, and feature order are independent of SolidCraft | Rust domain unit tests; no JSON imports in domain module |
| API-04 | One CAD operation maps to multiple SolidCraft commands | adapter tests: box, rounded outer vertical edges, through-holes |
| API-05 | Face/edge selection, workplane placement and feature IDs remain stable after model changes | live SolidCraft topology/feature tests before promoting selectors |
| API-06 | Typed physical dimensions prevent confusion between mm and inches | Rust unit conversion / input-validation tests |
| API-07 | Reusable, named part and sketch definitions can map to native SolidCraft features | design now, runtime and history qualification later |
| API-08 | `Faces::Top` and a CAD workplane become a native face-attached SolidCraft sketch | offline adapter tests, then Windows native geometry/history qualification |

## Architecture decision

Keep **four separate responsibilities**:

```text
CAD intent API (Part, geometry, selectors)
             -> SolidCraft adapter (feature planning and topology mapping)
             -> command transport (script / GUI / MCP)
             -> SolidCraft engine (the only source of actual geometry)
```

The prior 1:1 Rust method-to-command wrapper is only the lower-level baseline.
See [CAD API concepts](05-cad-api-design.md). The first implemented semantic
subset is a centered box, four original outside vertical-edge fillets, and
through-holes along Z. Do not claim general topology selection or editable
parameter propagation before qualifying it.

## Evidence

[Offline CI results](06-verification.md) demonstrate source compilation, unit tests and JSON generation only; neither a SolidCraft CAD export nor GUI integration has been qualified yet.

## Decisions

- Start with native Windows execution; treat **Python and Rust as candidate client languages**, not competing CAD engines.
- Only introduce a local Dockerfile for a concrete reproducibility need.
- Keep PartCAD exploration in a different experiment, proposed `exp.2026-012.partcad-solidcraft`.
- Never substitute STEP geometry for proof that a SolidCraft *design history* remains editable.
- Preserve third-party licensing and provenance; no vendor copy is needed for the initial experiment.

## Explicitly out of scope

- CNC toolpaths or running G-code from `scraftcnc`;
- general-purpose SolidCraft framework/tooling released to other projects;
- migration of OpenSCAD models;
- a shared `docker.cad-toolchain` repository.
