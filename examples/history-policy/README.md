# History policy and explicit Sketch experiment

This directory explores issue #13. Nothing here is a committed public API yet.

## 1. AUTO: semantic object, native feature

```python
boss = Boss(d=12.0, h=10.0, hole_d=4.0).attach(
    body,
    parent=Anchor.TOP,
    offset=(X.MIN + 15.0, Y.CENTER),
)
body = body + boss
```

The compiler keeps the semantic `Boss` as SolidCraft's native
`plastic.boss` feature.

## 2. Scoped compiler policy

```python
with behavior(history=History.SKETCH):
    boss = Boss(d=12.0, h=10.0, hole_d=4.0).attach(
        body,
        parent=Anchor.TOP,
        offset=(X.MAX - 15.0, Y.CENTER),
    )
body = body + boss
```

The Python object is still `Boss`. Only its compiled history changes.

The prototype lowers this to:

```text
Boss sketch
Boss extrude
Boss hole sketch
Boss hole cut
```

The policy scope must not leak to objects created afterwards.

## 3. Explicit Sketch scope

```python
with Sketch(name="Explicit pad", on=body, parent=Anchor.TOP) as sketch:
    sketch.add(Circle2D(d=10.0), offset=(0.0, -15.0))

pad = sketch.extrude(6.0)
body = body + pad
```

This is intentionally different from a compiler policy. Here the author says
that the sketch itself is part of the design and should remain visible in CAD
history.

The first prototype supports only an XY sketch containing `Circle2D`
profiles. It is enough to evaluate the Python structure, not a complete sketch
API.

## Design question

The main question is not whether all geometry should use sketches. It is how
SCPF should let the author choose between:

- semantic intent with automatic/native lowering;
- a scoped preference for sketch-based history;
- an explicitly authored sketch.

See GitHub issue #13 for the open API questions.


## Follow-up example: electronics enclosure

`reference/enclosure_steps.json` preserves a supplied SolidCraft/MCP enclosure
sequence as a second, more realistic history-policy example.

It deliberately mixes:

- an explicit constrained `Outline` sketch and parameter-driven extrusion;
- fillet + shell;
- an explicit side sketch for a USB-port cut;
- four native `plastic.boss` features;
- a final `width` change from 80 to 100 mm to exercise associative rebuild.

This is useful because not every feature should be forced into the same history
style. The two authored sketches should stay explicit, while the bosses are a
good target for comparing `AUTO` with `History.SKETCH`.

Keep this as a follow-up fixture until the minimal history-policy API is agreed;
do not broaden the first implementation just to reproduce the whole enclosure.
