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

## Test implementation

Qualification tests use Python's standard `unittest` framework.

The source order is deliberately optimized for review:

```text
imports
constants
TestCase classes
helper/parsing functions
if __name__ == "__main__":
    unittest.main()
```

The testcase therefore shows the expected behaviour before the reader reaches
the implementation helpers. Native TestCase classes are skipped when
`SCPF_NATIVE_ROOT` is absent; the heavy SolidCraft workflow supplies that
evidence path and reruns the same unittest suite.

The workflow itself only orchestrates SolidCraft commands and evidence files.
Functional assertions belong in `qualification/tests/`, not in shell/JQ when
they can reasonably be expressed in Python.

## Published results

Native evidence is first written under `output/native/<case>/`. After a
source-matched qualification run, `site/build.py` publishes that evidence to
GitHub Pages.

Two views are available:

- `/qualification/results/` — compact overview of every case, status,
  SolidCraft version, body count, parameter count and evidence count;
- `/qualification/<case>/` — measured parameters, body bounding boxes,
  mutation measurements, snapshot and direct links to the retained JSON/SC/STEP
  evidence.

The CI artifact remains the complete archive; Pages is the review surface.

## Qualification levels

- Q1 — Python API contract
- Q2 — generated SolidCraft command contract
- Q3 — native SolidCraft build
- Q4 — native measurement
- Q5 — saved-design parametric mutation
- Q6 — native visual artifact
