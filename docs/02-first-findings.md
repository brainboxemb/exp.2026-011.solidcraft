# 02 — Findings from source inspection

**Status: source reviewed; no SolidCraft installation or GUI/CLI run verified.**

## Which Python interface?

The [scraftcnc bindings](https://github.com/waynegramlich/scraftcnc/tree/main/scraftcnc/pybind) are usable separately from scraftcnc's CNC toolpath generator. They expose one Python method per SolidCraft engine command:

- `PyBind` with a `ControlTransport` for visible interactive modeling;
- `PyBind` with a `HeadlessTransport` using `solidcraft-cli mcp --headless`;
- a generator that derives command methods from the SolidCraft CLI metadata.

This is a stronger starting point than implementing a separate JSON/MCP client immediately.

## Windows-specific issue discovered

In upstream binding version 0.2.0, `control_dir()` knows Linux's default token location, but not Windows'. SolidCraft's [control protocol](https://github.com/tangency-labs/solidcraft/blob/main/docs/control-protocol.md#token) specifies:

`%LOCALAPPDATA%\\SolidCraft\\control\\PORT.token`

Without `SOLIDCRAFT_CONTROL_DIR`, `ControlTransport` may fail before sending a command to a Windows GUI. The experiment's Python example sets the correct folder when running on Windows and respects any explicit user override. This is a *local experiment adaptation*, not a verified upstream fix.

## Version question

- Current upstream binding cache: SolidCraft CLI **0.20.0**.
- Current stable SolidCraft when this experiment started: **0.30.1**.

Run live tests before relying on generated parameter names. If there are differences, record which commands failed and regenerate the binding from the locally installed CLI in a separate comparison before considering an upstream patch.

## Initial repeatable checks

`python -m unittest discover -s tests -v` uses a fake CAD object to verify command order, geometry parameters, error handling for invalid dimensions, and that extrusion receives the outline curve identifiers.

**Offline status:** five tests have been added, but have not been run in this connected GitHub session. Even when they pass, they will verify only the command sequence, *not* the actual SolidCraft runtime.

## Outside the Python binding

[partcad/partcad-solidcraft](https://github.com/partcad/partcad-solidcraft) solves a different problem: using SolidCraft as a PartCAD part type, converting designs to STEP/OCP shapes, and exporting PartCAD objects to native SolidCraft containers. Its STEP-based import loses native design history on the PartCAD side; therefore native parametric editing should be tested separately. Keep that in proposed Experiment 012, not in this experiment.

Docker stays deferred until a concrete headless reproducibility testcase needs it.
