# Forge functional API qualification

Forge is documented and qualified from **use scenarios**, not from internal
implementation details.

Each case document is first a functional description of one API behaviour.
The executable fixture and native SolidCraft checks then prove that Forge
actually implements that behaviour.

## Case structure

Every non-trivial case uses the same order:

1. **Use scenario** — what the model author is trying to achieve.
2. **Expected behaviour** — observable behaviour of the Forge API.
3. **Forge API** — the public Python expression used to describe it.
4. **Semantics** — what concepts such as anchor, frame, offset or parameter
   mean in this scenario.
5. **SolidCraft mapping** — how Forge lowers the intent to native commands.
6. **Acceptance criteria** — what must be true in the native model.
7. **Parametric change** — where relevant, what must happen after editing a
   saved SolidCraft parameter without rerunning Python.
8. **Verification evidence** — command JSON, native measurements and snapshot.
9. **Reference models** — BOSL2, OpenSCAD or PythonSCAD comparisons where they
   clarify the API design.

The fixture is therefore evidence for the API contract, not the definition of
the contract itself.

## Qualification levels

- Q1 — Python API contract
- Q2 — generated SolidCraft command contract
- Q3 — native SolidCraft build
- Q4 — native measurement
- Q5 — saved-design parametric mutation
- Q6 — native visual artifact
