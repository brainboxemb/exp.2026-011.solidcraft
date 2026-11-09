> **Historical / low-level boundary:** This page documents the first Rust
> implementation, a one-to-one SolidCraft command wrapper. It is **not**
> the intended high-level CAD API. See [Semantic CAD API and CadQuery
> design](05-cad-api-design.md) and the [domain model and adapter](../rust-facade/).
>
# 04 — Rust facade inspired by vcad's API design

**Scope clarification:** [`vcad`](https://docs.rs/vcad/latest/vcad/)
is used only as an **API-design reference** (fluent, typed,
code-first methods). This experiment **does not use vcad's CAD kernel**
and will not export or convert vcad models.

## Intended layering

```text
model written against a readable Rust interface
                     |
                     v
             SolidCraft<B>
              parameter()
              sketch()
              closed_polygon()
              finish_sketch()
              extrude()
                     |
                     v
           B: CommandTransport
              execute(id, params)
                     |
             +-------+-------+
             |       |       |
          script     GUI     MCP
             |       |       |
             +-------+-------+
                     |
                     v
               SolidCraft
           (one CAD engine)
```

We want callers to write something concise:

```rust
let mut cad = SolidCraft::new(ScriptTransport::default());
cad.parameter("width", "60 mm")?
   .sketch("XZ", "Bracket")?
   .closed_polygon(&points)?
   .finish_sketch()?
   .extrude("width", Direction::Negative, "Bracket")?;
```

This API is **implemented in the small Rust
[proof of principle](../rust-facade/)**; the initial backend collects
native SolidCraft commands into a script. No separate geometry
algorithm is implemented.

### Command mapping (single source of truth)

| Facade call | SolidCraft command |
|---|---|
| `parameter("width", "60 mm")` | `parameters.change` |
| `sketch("XZ", "Bracket")` | `sketch.create` |
| `closed_polygon(points)` | `sketch.line`, `closed:true` |
| `finish_sketch()` | `sketch.finish` |
| `extrude(...)` | `solid.extrude` |

The mapping follows [SolidCraft's own bracket
script](https://github.com/tangency-labs/solidcraft/blob/main/examples/bracket.json).

### What this first PoP establishes

The **design** separates the public API from how commands are delivered.
The ScriptTransport can emit native JSON without an installed
SolidCraft binary. The API also validates basic inputs and propagates
errors rather than hiding failures.

### What changed

A separate **semantic CAD module** is now implemented for a small subset.
It owns Part/holes/edge selections, while a SolidCraft-specific adapter emits
multiple command steps per feature. The old wrapper on this page is retained
as a transport/command-layer reference and should not be extended as the
public CAD API.

### What still needs implementing and testing

- A `ControlTransport` to reach a running Windows SolidCraft GUI with
  its per-session authentication token.
- A headless MCP transport, including initialization and tool replies.
- Typed sketch/feature handles that use real SolidCraft response IDs.
- Higher-level API ergonomics (sketch builders, enum/units, fillet,
  selection semantics) backed by actual SolidCraft commands.
- Real `cargo test` and live CLI/GUI runs, including native file
  save/reopen; this runtime is not available in the connected environment.

**Do not present a JSON script fixture as proof of working live GUI or
MCP integration.** Keep the facade implementation small until we have
those results.
