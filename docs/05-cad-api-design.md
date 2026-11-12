# Python CAD API design

SCPF exposes CAD objects, not JSON commands, transports, or an independent
geometry engine.

## User-facing model

A model does not need `@dataclass`. Numeric class fields are model
parameters:

```python
class Enclosure:
    length = 80.0
    width = 50.0
    height = 30.0
    wall = 2.0
```

```python
holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
    count=2, spacing=self.width - 24, axis=Axis.X
).on(plate, face=Faces.TOP)
plate = plate + holes

boss = Cylinder(d=24, h=14).on(plate, face=Faces.TOP)
plate = plate + boss

bore = Hole(d=12, depth=Depth.THROUGH_ALL).on(
    plate, face=Faces.TOP)
plate + bore
```

## Parameter intent

Numeric names are part of the user-facing API contract:

| Python name | Meaning | Native SolidCraft parameter |
| --- | --- | --- |
| `WIDTH = 100.0` | fixed constant | no |
| `_pitch = 160.0` | Forge/build-time input | no |
| `width = 100.0` | editable model parameter | yes |

A public model parameter that disappears before native compilation is suspicious.
Forge emits `ModelParameterWarning` instead of silently pretending the design
is still associative. Use `pv()` only where Python genuinely needs a concrete
number; if that is the *only* use of a public parameter, either preserve the
symbolic dependency or rename the input with a leading underscore.

Nested components do not publish all their defaults automatically. Explicit
parent binding is preferred when several parts must share one model parameter:

```python
bottom = BottomBoard(corner_radius=self.corner_radius)
roof = RoofBoard(corner_radius=self.corner_radius)
bracket = Bracket(inside_corner_radius=self.corner_radius)
```

All three native fillets then depend on the same `corner_radius` parameter.
A component default that should be independently public can be selected with
`include=("name",)`; it can be given an explicit shared model name with
`include={"local_name": "model_name"}`.

## Semantics

- `on(target, face=Faces.TOP)` is the simple within-component placement
  mechanism for a feature on a selected surface.
- For a Hole, `face=Faces.TOP` means drilling starts at the current top
  surface and proceeds inward.
- `attach()` is reserved for explicit attachment relationships between
  reusable components in an assembly. It is the public Forge relationship;
  SolidCraft `joint.create` remains an internal lowering detail.
- `+` adds the described CAD feature to the model; for Hole intent the
  resulting SolidCraft operation is a cut.
- The adapter decides the native representation. For Sample Plate it creates
  the editable `Holes` and `Bore` sketches and cut extrusions.
- Python scripts do not need an explicit `Sketch` object.
- `Faces` selects a surface, including the surface used by `on()`.
  `Anchor` describes explicit assembly attachment references. They are
  intentionally separate concepts.
- Component anchors may identify a face (`RIGHT`, `TOP`, etc.) or one of
  the eight rectangular corners such as `FRONT_TOP_RIGHT`. Corner anchors
  lower to native SolidCraft edge/corner origins, so saved-model parameter
  edits can move the referenced corner and the attached component together.
- `shell()` is a modifier like `fillet()`: for example
  `body.shell(2, open=Faces.TOP)`.
- `Lip`, `SnapFit`, `Boss` and `Rest` are ordinary object-level
  building blocks, like `Box`, `Cylinder` and `Hole`; the compiler maps
  them to native SolidCraft plastic features.
- `Anchor.INNER_BOTTOM` refers to the inner floor of a shelled body,
  so enclosure details can be placed relative to the shell wall instead of
  hard-coded world Z coordinates.
- `X.MIN/CENTER/MAX` and `Y.MIN/CENTER/MAX` describe placement relative
  to the corresponding parent bounds. For example
  `offset=(X.MIN + 10, Y.MAX - 6)` means 10 mm from the minimum X edge
  and 6 mm from the maximum Y edge.

## Responsibility boundaries

```text
Python objects (SCPF)
  -> semantic compiler
  -> SolidCraft commands
  -> SolidCraft BRep, parameters and editable feature history
```

Never silently treat numeric coordinates as robust long-lived face
references. Native save/reopen and parameter-edit tests determine which
anchors are truly associative.
