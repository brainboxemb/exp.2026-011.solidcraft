# 03 — Choosing a scripting interface

SolidCraft already has a language-independent **engine command API**.
The same commands are accessible as JSON scripts, through its CLI, over the
desktop control port, and via MCP.

## Our options (in increasing integration complexity)

| Option | Requires custom bindings? | Best suited to |
|---|---|---|
| JSON command script | No | First CLI smoke test and reference fixture |
| Python -> JSON -> `solidcraft-cli run` | No | Small reproducible parametric generators with a short Python script |
| Python with `scraftpybind` | Existing unofficial bindings | Interactive GUI control, inspection, return values and headless sessions |
| Python with our own tiny JSON/MCP client | Yes, modest effort | Only if the upstream binding has important compatibility problems |
| Lua invoking JSON/CLI | A custom wrapper | Possible, but no apparent native Lua scripting runtime in SolidCraft |
| Rust calling CLI/JSON API | A small wrapper, just as in Python | Good if the controlling application is already written in Rust; more build overhead for tiny scripts |
| Rust directly using SolidCraft internal crates | A Rust crate dependency rather than a command wrapper | Potentially powerful, but in-process integration is not a stable public scripting interface by default |

**Native plugins are not a ready route:** [the SolidCraft plugin RFC](https://github.com/tangency-labs/solidcraft/blob/main/docs/rfcs/0002-plugins.md) proposes WebAssembly components, with Rust as the first language. It explicitly says the plugin host and executable plugins are not implemented yet. That RFC is not evidence of supported Lua or stable Rust plugin scripting today.

## Important distinction: language versus CAD engine

"Python is easier than Rust" was too general. Python is a low-friction way to
automate **the already installed SolidCraft desktop program** (JSON, CLI,
control port, MCP). Rust can send exactly the same commands; neither language
has a fundamental capability advantage at this boundary. For a short local
experiment, Python is convenient because it runs without a Cargo project and
recompilation. For a reusable, typed application or a native Rust CAD crate,
Rust may be the simpler design.

[`vcad`](https://docs.rs/vcad/latest/vcad/) is an important counterexample:
it provides *direct Rust CAD methods*, not just a wrapper around another
program's command API. See [vcad alternative](04-vcad-rust-alternative.md).
That is a comparison of **two CAD systems/engines**, not just two scripting
languages. A `vcad` model does not automatically become an editable
SolidCraft feature timeline; exchanging STEP/STL normally exchanges resulting
geometry, not all original modeling operations.

## Try both small Python paths

### A. No bindings; Python emits a script

```powershell
python .\examples\python_cli_script.py
python .\examples\python_cli_script.py --run
```

The first command writes `output/bracket.json` without SolidCraft installed.
The second invokes `solidcraft-cli run output/bracket.json --out output/bracket.step`.
It follows the published [SolidCraft script format](https://github.com/tangency-labs/solidcraft/blob/main/docs/scripts.md) and the command structure of the upstream [bracket example](https://github.com/tangency-labs/solidcraft/blob/main/examples/bracket.json).

This fixture defines cross-section dimensions in Python and uses the native SolidCraft `width` parameter for extrusion. This does **not** prove all dimensions persist as editable native CAD parameters; that is a separate qualification case.

### B. Existing bindings; Python calls CAD methods

`examples/plate.py` calls the existing `PyBind` command methods, using a
headless MCP session or the visible GUI. This path additionally processes
command responses and retains a live session.

Do **not** duplicate `scraftpybind` without a measured requirement.

## Recommendation

Start with the smallest Python-to-JSON script to confirm what SolidCraft
does, then evaluate `scraftpybind` for a live interactive Python session.
If command compatibility proves unreliable, compare against a **tiny local
Python transport** instead of taking on a new scripting language.

We are **not yet qualifying** these examples as successful runs with
SolidCraft 0.30.1. Installation and runtime checks remain outstanding.
