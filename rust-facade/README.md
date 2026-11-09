# Rust facade PoP (SolidCraft remains the CAD engine)

This is **not a vcad integration** and does not implement a modeling kernel.
It is a small example of a pleasant, type-aware Rust API mapping calls to
SolidCraft's documented **command IDs and JSON arguments**.

## Run

From `rust-facade/`:

```powershell
cargo test
cargo run
cargo run -- --run
```

- `cargo test` checks command mapping and invalid geometry inputs.
- `cargo run` emits `../output/rust-bracket.json` with no SolidCraft runtime.
- `cargo run -- --run` also invokes `solidcraft-cli run` to export STEP.
  This last mode requires an installed CLI on `PATH`.

The current ScriptTransport **queues** commands. It cannot return
SolidCraft-generated curve/feature IDs. To model more complex parts
interactively, implement the same CommandTransport trait against the GUI
control port or headless MCP and propagate real JSON results; add typed
handles only when the response format has been verified.

The syntax was reviewed as source; **no Rust compiler is available in
the connected build environment**, so compilation and runtime results
are still outstanding. The planned acceptance work stays in
[Experiment 011](../docs/00-plan.md).
