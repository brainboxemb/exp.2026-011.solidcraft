# Parameterized Box

## Use scenario

A model author wants a simple rectangular solid whose length, width and height
remain editable parameters in SolidCraft.

## Expected behaviour

Changing one of the public model dimensions must change the corresponding
native dimension without requiring special Forge syntax.

## Forge API

```python
class SimpleBox:
    length = 40.0
    width = 30.0
    height = 10.0

    def build(self):
        return Box(self.length, self.width, self.height)
```

## Semantics

Public lower-case numeric fields are model parameters. `Box` is geometry
intent; Forge does not become the geometry kernel.

## SolidCraft mapping

Forge emits native parameters and lowers the box through SolidCraft's native
sketch/extrude path.

## Acceptance criteria

- one native solid exists;
- dimensions are 40 × 30 × 10 mm;
- the native timeline contains no errors;
- the dimensions remain named editable parameters.

## Parametric change

This base case does not perform a saved-design mutation. Parameter mutation is
qualified in the dedicated parameter/attachment cases.

## Verification evidence

Fixture: `examples/simple-box/scpf/model.py`

CI retains generated command JSON, native results, measurements, STEP, saved
SolidCraft design and snapshot.

## Reference models

**OpenSCAD:** `cube([40,30,10])` is the constructive-geometry baseline.
Forge differs by retaining native editable SolidCraft history.
