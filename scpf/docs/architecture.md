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

Symbolic dimensions must survive into native geometry regardless of the
operation direction. In particular, `Polygon2D` coordinates containing
model parameters stay as SolidCraft expressions for positive, negative and
symmetric extrusions; extrusion direction must not silently freeze an
otherwise editable profile.

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

## Parameter intent: constant, build input or native model parameter

SCPF uses Python naming to make a dimension's intended lifetime visible in the
model source:

```python
class Display:
    PANEL_COUNT = 5          # fixed constant
    _panel_pitch = 160.0     # Forge/build-time input
    opening_width = 844.0    # native SolidCraft model parameter
```

- **`UPPER_CASE`** numeric class attributes are fixed constants. They are
  available to `build()`, but they are not model inputs and are never emitted
  as SolidCraft parameters.
- **`_lower_case`** numeric fields are Forge/build-time/private inputs.
  Their own numeric defaults stay concrete and are not published as model
  parameters. When a parent assembly explicitly passes a `Parameter` or
  expression into such an input, however, that parent dependency stays
  symbolic. This allows parent-owned placement/datums without turning them
  into public parameters of the reusable part.
- **`lower_case`** numeric fields are public model parameters. Forge expects
  them to survive into native SolidCraft expressions and remain editable.

If a public model parameter is consumed only by Python, for example through
`pv()` or a non-associative occurrence placement, SCPF emits
`ModelParameterWarning`. Forge also warns when a parameter is **partly**
native but is simultaneously flattened into a concrete
`occurrence.move()`/rotation value. In that case changing the parameter in
SolidCraft would update only part of the design. This is deliberate: a
parameter visible in the model source should not silently stop being fully
parametric in SolidCraft.

A reusable component file is also a standalone SCPF model when it contains
exactly one public class with `build()`. SCPF selects that class directly:

```python
# components/corner_bracket.py
class CornerBracket:
    ...
    def build(self):
        ...
```

So the same source can be run with:

```text
python -m scpf components/corner_bracket.py --connect
```

There is no launcher file and no trailing `CornerBracket()` required. If a
file contains multiple public model classes, automatic root selection is
deliberately disabled; an explicit final model call must choose the root.

Reusable components use the same implicit parameter intent as root models.
Public lower-case numeric defaults become editable component-local parameters.
Forge namespaces those local names when component definitions share a design.

A parent model can couple a child input directly to one of its parameters:

```python
Bracket(
    bracket_width=self.bracket_width,
    inside_corner_radius=self.corner_radius,
)
```

Both child dimensions then use the existing native parent parameter names.
Passing a parent `Parameter` or `Expression` is a binding to that dependency,
not a request to create a second component parameter. Private underscore
defaults remain concrete build-time inputs and upper-case values remain fixed
constants.

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


## Forge qualification levels

Forge changes are qualified in layers. A green Python test alone is never
treated as proof that SolidCraft produced the intended CAD result.

| Level | What is verified | Typical evidence |
| --- | --- | --- |
| Q1 — Python API | Public API behavior, validation, symbolic-expression handling and compiler invariants | `unittest` results |
| Q2 — command contract | Complete example scripts compile to valid, inspectable SolidCraft command JSON | generated `*.json`, command counts |
| Q3 — native build | The pinned tested SolidCraft runtime accepts the command plan and creates a saved editable design | `results.json`, `model.sc`, version-specific plain `model.json`, STEP |
| Q4 — native measurement | Actual bodies/timeline are evaluated after construction | `measurements.json`, bounding-box assertions |
| Q5 — parametric mutation | A saved design is edited with `parameters.change`; dependent geometry/joints must re-solve without recompiling Python | parameter export, changed `*.sc`, second measurement set |
| Q6 — visual artifact | Native snapshots make orientation and placement regressions reviewable by a human | PNG snapshot |

The CI qualification artifact must retain the generated commands and native
results, not only a pass/fail flag. For assembly/anchor work in particular,
the report should show both the generated `joint.create` parameters and the
measured native result after at least one parameter mutation.

Native design JSON is retained as evidence for the exact tested SolidCraft
runtime. Qualification should prefer public commands such as
`parameters.export`, `parameters.change` and `eval` for assertions rather
than depending on undocumented internal design-file keys. A new SolidCraft
version must rerun the native qualification before Forge carries Q3-Q5 claims
forward to that version.

### Qualification fixture rules

Fixtures should isolate one concept at a time. Keep geometry deliberately
simple unless geometry itself is the feature under test. For example, the
`bracket` fixture is a plain extruded L-profile: no holes, fillets or shell
operations. More complex assembly fixtures may reuse that component, but a
failure in an attachment test must not be confounded by unrelated feature
history.

A new Forge API or lowering feature is not considered ready for CAD-project
use until it has:

1. a focused Q1 regression;
2. a self-contained Q2 fixture;
3. a Q3/Q4 native SolidCraft check;
4. Q5 coverage when the feature claims associativity/parametric behavior;
5. a Q6 snapshot when orientation or spatial placement is material.

The HUB75 model is therefore a downstream integration consumer, not the place
where Forge attachment semantics are discovered experimentally.


### Qualification case sheet

Every non-trivial Forge qualification case should explain the complete path,
not only assert a final number. Use the following structure in test comments,
fixture documentation or the generated qualification report:

1. **Intent** — the user-level CAD operation being expressed.
2. **Forge API** — the exact public Python calls used by the fixture.
3. **Forge model** — the internal objects/relations that should result.
4. **SolidCraft lowering** — the native command(s) and parameter fields that
   Forge is expected to emit.
5. **Native expectation** — the measurable geometry/placement SolidCraft must
   create.
6. **Parametric mutation** — which saved-design parameter is changed and which
   native relation must update without rerunning Python.
7. **Evidence** — command JSON, timeline/results, measurements and snapshot.
8. **Reference model** — where useful, compare the concept with BOSL2,
   OpenSCAD or PythonSCAD and state explicitly where Forge differs.

The reference comparison is conceptual, not an API-compatibility promise.
Forge should use familiar CAD vocabulary when it helps users understand the
model, but its lowering must follow SolidCraft's native capabilities.

#### BOSL2 as an anchor/attachment reference

BOSL2 is particularly useful for terminology around **anchors** and
**attachment frames**. Its attachable model separates several ideas that are
also valuable in Forge:

- an **anchor** selects a meaningful point/region on an object;
- orientation is part of the attachment context rather than merely an XYZ
  coordinate;
- attachment is evaluated in the **local coordinate system at the parent
  anchor**, not blindly in world coordinates;
- named anchors may expose application-specific datums while generic anchors
  cover common sides, edges and corners.

Forge does not need to reproduce BOSL2's implementation. The comparison is a
design check: when Forge uses the word `Anchor`, tests should make clear
whether it means only a point, a point plus orientation, or a topology-backed
native SolidCraft reference.

Useful external references:

- BOSL2 attachment overview:
  https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Overview
- BOSL2 basic positioning (anchor, spin, orient):
  https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Basic-Positioning
- BOSL2 attach behavior and parent-local coordinate system:
  https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Attach

#### OpenSCAD and PythonSCAD comparisons

OpenSCAD remains useful as the baseline for explicit constructive geometry:
translations, rotations, unions/differences and parameter-driven source are
easy to reason about because transforms are visible in the program text.
Qualification notes may show an equivalent OpenSCAD expression when that
makes Forge semantics clearer.

PythonSCAD comparisons are useful primarily for **Python API ergonomics**:
how a Pythonic model represents transforms, reusable objects and composition.
Forge should only adopt those patterns when they remain a thin, predictable
translation to SolidCraft rather than becoming a second CAD kernel.
