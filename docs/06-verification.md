# 06 — Verification

## Offline Rust checks

CI compiles the Rust crate, runs all Rust tests, generates the semantic plate command plan and compares it with [`fixtures/plate-top-face.json`](../fixtures/plate-top-face.json).

## First SolidCraft 0.30.1 runtime result

The first native CLI run reached **solidcraft-cli 0.30.1** and failed at the face-attached sketch:

```text
step 6 (sketch.create): invalid parameters for sketch.create:
an exact face pick requires both body and index
```

The adapter supplied a face point plus a body name but no face index.

SolidCraft allows either:
- a **point-only** face pick that resolves uniquely; or
- an **exact** pick with both body and face index.

We must not invent a face index. The next adapter change should use a point-only pick for this single-body PoP and rerun the pinned runtime workflow.

## Still to qualify

- successful SolidCraft execution
- STEP dimensions and geometry
- hole placement/workplane orientation
- fillets
- editable native `.sc` history
- GUI and MCP transports
