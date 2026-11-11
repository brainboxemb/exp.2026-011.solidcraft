# How SCPF works (without building a second CAD engine)

SCPF is a **Python interface** to SolidCraft. It does not draw meshes,
rotate solids itself or solve geometry. SolidCraft does that.

The principle is simple:

> Python describes *what you want*. SCPF translates that description
> into native SolidCraft commands. SolidCraft builds and places the parts.

## A practical example: one component, two placements

Suppose you want two panels next to each other.

```python
from scpf import Box, component

class Panel:
    def build(self):
        return Box(160, 320, 14.5)

PanelComponent = component(Panel)

class Pair:
    def build(self):
        left = PanelComponent().rotate(axis=(1, 0, 0), degrees=90)
        right = left.copy().move(x=160)
        return left + right

Pair()
```

**What this means:**

- `Panel` describes one physical part and its editable features.
- `left` and `right` are two *occurrences* of that one part.
- The two occurrences can be placed independently.
- Changing the shared definition changes both occurrences.

**What SCPF sends (simplified):**

1. `component.create("Panel")` — define the reusable part.
2. Native shape/feature commands — construct the panel once.
3. `occurrence.copy("Panel")` — create the second placement **at the origin**.
4. `occurrence.move("Panel:1", axis=[1,0,0], angle="90 deg", translate=[0,0,0])`.
5. `occurrence.move("Panel:2", axis=[1,0,0], angle="90 deg", translate=[160,0,0])`.

All five steps use **native SolidCraft functionality**. SCPF only
organizes the commands and their parameters.

Creating copies *before* moving the first occurrence is deliberate.
If a copy were made from an already rotated part, SolidCraft would inherit
that earlier placement and a second move could then have an unintended
effect. Starting every occurrence at the origin avoids that problem.

## Who is responsible for what?

| Task | Responsible |
| --- | --- |
| Model classes, reusable definitions, `copy()` | SCPF |
| Check numeric values and reject invalid input | SCPF |
| Convert native shape/feature operations into command JSON | SCPF |
| Create sketches, solids, fillets, bores and materials | SolidCraft |
| Apply rotations and translations to occurrences | **SolidCraft** |
| Calculate geometry, volume and bounds | **SolidCraft** |
| Save native models, STEP files and screenshots | **SolidCraft** |

SCPF contains simple dimension arithmetic where it is necessary to
describe *where* a feature belongs. For example, it can calculate
a corner's coordinate from a rectangular part's width. That is different
from inventing a geometry engine.

Some modules import `math.isfinite`. This is a simple input check:
it rejects invalid values such as `NaN` or infinity. It does
**not** rotate or construct geometry.

## Design rule: don't reimplement the CAD engine

For occurrence placement SCPF deliberately does **not** implement:

- 4×4 matrix multiplication;
- inverse matrices;
- trigonometric rotation calculations;
- custom orientation fixes after a native rotation.

If SolidCraft offers a native command for the requested operation,
use it. A Python wrapper should make that operation **easier to read**,
not introduce another competing implementation.

This rule does not forbid small, clearly named calculations that
express the dimensions of a design.

## What is supported now?

**Movement**: `move(x, y, z)` adds a displacement to a Python
occurrence's intended position. When compiled, the native occurrence
is moved once to that final position.

**Rotation**: `rotate(axis=(...), degrees=...)` sets one axis-angle
orientation for a Python occurrence. Calling `rotate()` again
**replaces** the earlier orientation. It is not a chain of rotations.

**Copies**: Python `copy()` inherits the source object's intended
position and orientation. The native compiler creates the copies
unplaced and positions them individually.

**Groups**: `.group("Name")` creates a real parent component in the
SolidCraft browser.

**Attachments**: some rectangular face-to-face attachments are
supported. They have a limited reference-based positioning system.
This is **not** a full native mating solver.

## What went wrong in the HUB75 experiment?

The first implementation sent `occurrence.move` with a newer
`to` parameter. SolidCraft **0.30.1** did not support it. Earlier
runs could accept the command without applying the rotation.

The next implementation calculated translation and rotation matrices
in Python. That added complexity without solving a missing SolidCraft
feature. It also confused two different matrix layouts and caused a
native command error.

The simpler approach is to use the existing `translate`, `axis`,
and `angle` parameters and to create the copies before placing them.

## How to verify a change

There are **two different checks**, and both are important.

**1. Python library tests:** verify that the generated commands are
correct, readable and ordered as expected. For example, check that
every `occurrence.copy` comes before the first `occurrence.move`.

**2. Native SolidCraft verification:** execute the generated commands
with SolidCraft **0.30.1**, inspect the saved occurrence transforms
and check the actual model dimensions and front/rear views. A
successful JSON parse does **not** prove that the model is upright.

The CAD project runs these native checks separately. Do not mark a
geometry bug fixed solely because Python unit tests pass.

## Remaining design boundaries to review

- **`rotate()` is not compositional.** If the caller wants two
  sequential rotations, the API should eventually express that clearly.
  Until it does, do not pretend two calls compose.
- **Rectangular anchors perform simple coordinate arithmetic.**
  Keep the supported scope explicit, and prefer native references
  when SolidCraft can provide them.
- **Occurrence grouping and attachments** must be tested in native
  SolidCraft, especially when the parent component is placed or rotated.
- **Version detection:** the local `solidcraft-cli --version` tells
  us which CLI is installed; it does not guarantee that a separate
  running GUI is the same version. Warn rather than claiming certainty.

Further reading: the [API Guide](https://brainboxemb.github.io/lib.py.solidcraft/guide/)
and the [CAD models and native verification results](https://brainboxemb.github.io/2026-011-02.cad.solidcraft/).
