# 03 — Choosing the language for a SolidCraft API facade

## What we actually want to build

**Not a new CAD engine.** The only modeling engine is SolidCraft.

We want an ergonomic API — similar in **shape and naming** to
[`vcad`'s Rust API](https://docs.rs/vcad/latest/vcad/) — that converts
high-level calls into SolidCraft commands.

For example, a user-facing Rust API could eventually look like:

```rust
let mut cad = SolidCraft::connect(...)?;
cad.sketch("XZ", "Profile")?
   .polygon(&points)?
   .finish()?;
cad.extrude("60 mm")?;
```

This is **illustrative API design**, not the API of SolidCraft and not
a claim that this exact code compiles. Below that facade, each action
maps to an existing SolidCraft command:

```text
Rust or Python facade
       |
       v
SolidCraft command objects / responses (JSON)
       |
       +--> CLI script for batch model creation
       +--> GUI control channel for interactive modeling
       +--> MCP headless session for automation
       |
       v
SolidCraft application / modeling engine
```

The facade must **not** implement CSG, extrusion, geometry kernels,
mesh conversion or independent model history. SolidCraft owns all of that.

## Python versus Rust for *this exact task*

| Criterion | Python facade | Rust facade |
|---|---|---|
| Calling CLI, JSON, GUI control or MCP | Straightforward | Straightforward |
| Rapidly testing command signatures | Faster iteration, no compilation | Build cycle |
| Typed public API (arguments, units, enums, errors) | Possible with type hints | Strong compiler-enforced types |
| Handling response IDs and feature handles | Ordinary Python objects | Rust types and ownership |
| Distributing a small script | Simple with Python available | Binary build and packaging |
| Reusable library with strong interface contract | Possible | **Compelling choice** |
| Native Rust SolidCraft internals | Not relevant | **Also not required** for external scripting |

So Python is only **faster to prototype** here. Rust is a perfectly
reasonable — perhaps preferable — choice if the goal is a carefully
defined reusable API rather than an ad-hoc script.

Lua could also send the command protocol, but it has no native advantage
for this task. The [SolidCraft plugin RFC](https://github.com/tangency-labs/solidcraft/blob/main/docs/rfcs/0002-plugins.md)
is still a separate, unfinished feature; we do not need plugins or
WebAssembly for an external wrapper.

## The interface boundary matters more than the language

Keep four components distinct:

1. **Facade**: names such as `sketch`, `extrude`, `fillet`,
   validation and unit-friendly parameter types.
2. **Command mapping**: exact SolidCraft command ID and argument JSON.
3. **Transport**: batch script, persistent GUI port or headless MCP;
   execute commands and pass errors/results back.
4. **SolidCraft runtime**: applies commands, creates actual geometry
   and preserves feature history.

Avoid conflating the source-language API with SolidCraft's engine.

The existing `scraftpybind` is a useful Python implementation of layers
2 and 3. Our potential Rust facade would be an alternative implementation
of those same boundaries, not a Rust CAD kernel.

## What to test

- Can a typed API produce the exact same commands as SolidCraft's
  published `examples/bracket.json`?
- Does the same API work with a static script transport and a live
  transport, without rewriting model logic?
- Are generated feature/sketch IDs correctly returned and reused?
- Can command failures be surfaced with useful typed errors?
- Can parameter expressions and native design history survive
  save/reopen in SolidCraft?
- What changes between SolidCraft CLI 0.20.0 and 0.30.1?

A [minimal Rust facade](../rust-facade/) now covers the **command
mapping / script transport boundary**; GUI and MCP transport support
remain separate qualification work.

## Existing Python baselines

- [Python to native JSON script](../examples/python_cli_script.py):
  no bindings; useful command reference.
- [`scraftpybind` Python experiment](../examples/plate.py):
  existing generated methods and live transports.

Both ultimately send SolidCraft commands.

## Recommendation

Develop the **API shape independently of the transport**, prototype
a few functions in Rust and Python, then judge the *clarity of the
interface*, not an assumed language ranking. Rust is absolutely viable
for a small typed command abstraction.
