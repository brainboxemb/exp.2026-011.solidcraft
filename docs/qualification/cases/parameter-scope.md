# Implicit component parameters and shared dependencies

## Use scenario

A user defines a reusable component with ordinary public numeric fields. Those
dimensions should be editable without an extra publication mechanism.

The same component is then used in four ways:

1. with its default width;
2. with a numeric width override;
3. twice with a width bound to one parent parameter;
4. with a width derived from that parent parameter.

The user should not need `include=`, aliases or a separate parameter API.

## Expected behaviour

```python
class Panel:
    width = 40.0
    DEPTH = 20.0
    HEIGHT = 10.0

    def build(self):
        return Box(self.width, self.DEPTH, self.HEIGHT)
```

A plain nested `Panel()` is treated as a reusable component and gets an editable component-local parameter.

```python
Panel(width=60.0)
```

A numeric override is still editable, but belongs to that distinct component
definition.

```python
Panel(width=self.shared_width)
```

A parent `Parameter` is inherited. Forge must reuse `shared_width`; it must
not create a second child parameter such as `Panel_width`.

```python
Panel(width=self.shared_width / 2)
```

The dependency remains symbolic as an expression of the same parent parameter.

## Naming rules

- public `lower_case` numeric field → editable native parameter;
- `_private_lower_case` numeric field → Forge/build-time input;
- `UPPER_CASE` numeric field → fixed class constant;
- parent `Parameter` / `Expression` passed to a child → inherited symbolic
  dependency, not a duplicate child parameter.

For reusable component definitions, local parameter names are namespaced by
Forge to avoid collisions, for example `Panel_width`.

## Q1/Q2 — Python and generated command JSON

The fixture must produce exactly these user parameters:

```text
Panel_width   = 40
Panel_2_width = 60
shared_width  = 80
```

The two direct shared children and the derived child must all reference
`shared_width`. There must be only one `parameters.add` for it.

Generated `commands.json` is retained as evidence.

## Q3/Q4 — native SolidCraft design

The same command JSON is executed with the pinned tested SolidCraft version.
Qualification retains:

- `model.sc` — reopen/save artifact;
- `model.json` — self-contained plain SolidCraft design JSON;
- `parameters.json` — public native parameter export;
- `measurements.json` — evaluated bodies and parameter values;
- STEP and PNG evidence.

The design JSON is evidence for that exact SolidCraft version. Forge does not
bind itself to undocumented internal design keys; machine assertions prefer
the public parameter/export/eval commands.

## Q5 — saved-design mutation

Without rerunning the Python model, change:

```text
shared_width: 80 mm → 100 mm
```

Initial body widths:

```text
40, 40, 60, 80, 80
```

Expected widths after the native parameter change:

```text
40, 50, 60, 100, 100
```

That proves:

- local component parameters remain independent;
- both direct child bindings follow one parent parameter;
- the derived expression `shared_width / 2` remains associative.

## Version contract

Native evidence is version-specific. The current tested runtime is SolidCraft
0.30.1. A newer SolidCraft version may change command contracts or the saved
design schema; it must pass this qualification again before Forge claims the
same Q3–Q5 status for that version.

## Reference models

**PythonSCAD** is the primary ergonomics reference: parameterized Python
objects should feel like ordinary Python objects rather than require a second
publication DSL.

**SolidCraft** is the native capability truth: saved user parameters and
expressions determine whether later edits really rebuild the model.
