# 06 — Verification and evidence

## Offline PoP, 9 November 2026

**Exact change:** `cf40297f9446767218f5e58020c4e312c7a63527` on
`feature/issue-1-python-interface`.

GitHub Actions workflow:
[CAD API / Rust PoP — successful push run](https://github.com/brainboxemb/exp.2026-011.solidcraft/actions/runs/42658989559).

| Check | Result | What it actually establishes |
|---|---|---|
| `cargo test --manifest-path rust-facade/Cargo.toml --all-targets` | **7 passed** | Rust source compiles; domain selection/validation and command-adapter unit assertions pass |
| `cargo run --manifest-path rust-facade/Cargo.toml --bin cad_plate` | **Passed** | The semantic API can generate a SolidCraft JSON script |
| `python3 -m json.tool output/cad-plate.json` | **Passed** | Generated file is syntactically valid JSON |
| `python3 -m unittest discover -s tests -v` | **8 passed** | Existing Python fixture command-shape tests pass |

The earlier CI run on commit `78e6827f1394fd02f14ca927f8f0d2782843e00d`
failed because the first assembled tree omitted `rust-facade/Cargo.toml`
(and the original `src/main.rs`). Both files were restored in the
qualified commit above. This was a repository assembly issue rather than
a SolidCraft geometry failure.

## Follow-up offline run after adding typed lengths and µcad references

[Successful push CI run](https://github.com/brainboxemb/exp.2026-011.solidcraft/actions/runs/42659957864)
on `da67439824ecb8ec955e6e986d754b0ae2f2bd0d` verifies
**8 Rust tests** and **8 Python tests** passing, including the new
explicit millimeter/inch conversion checks. Rust script generation and
JSON syntax verification also passed.

This is still a **source/command-fixture qualification only**.

## Face-attached workplane milestone

[CAD domain / SolidCraft adapter update](https://github.com/brainboxemb/exp.2026-011.solidcraft/commit/676a56d87bdf096e2632d94f2eac1028a2d221d1)
passed [offline CI](https://github.com/brainboxemb/exp.2026-011.solidcraft/actions/runs/42667955909).
The semantic `Faces::Top` feature now maps to a **native SolidCraft face source** on `sketch.create`, rather than the previous global XY plane. Offline tests verify the command plan; the actual face's local axes and model output remain unverified.

A [Windows qualification script](../scripts/qualify-solidcraft.ps1) can run the experiment against an installed SolidCraft CLI; it has not been executed on the user's computer.

## Canonical CAD script fixture

The latest [offline CI](https://github.com/brainboxemb/exp.2026-011.solidcraft/actions/runs/42668871056) checks the Rust-generated design command plan against the committed
[`fixtures/plate-top-face.json`](../fixtures/plate-top-face.json), *in addition to* compiling and running Rust/Python unit tests.

The [Windows qualification script](../scripts/qualify-solidcraft.ps1) now supports `-SkipBuild`: test the same semantic CAD fixture with the installed SolidCraft CLI **without requiring Rust**. This avoids making Rust installation a prerequisite for checking SolidCraft geometry.

## Not yet tested

- Running `solidcraft-cli run output/cad-plate.json --out output/cad-plate.step`
  on SolidCraft **0.30.1**.
- STEP file existence, size, bounding box, hole diameters and edge fillets.
- Whether SolidCraft accepts all adapter command arguments as expected.
- Editable native SolidCraft design/history and named parameters after save/reopen.
- GUI control port and headless MCP transports.
- General topology-based CadQuery-style `faces`/`edges` selectors.

**Important:** A green offline run is **not** evidence that a real
SolidCraft CAD model was constructed correctly. This remains a draft
experiment until these runtime checks are performed.
