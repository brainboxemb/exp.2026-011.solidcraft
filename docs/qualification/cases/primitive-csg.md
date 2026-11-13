# Primitive CSG and orientation

## Use scenario

A Forge user wants to combine basic solids directly: add a translated box to a
sphere, drill three orthogonal cylindrical bores and finally clip the result
with an intersection box.

This case deliberately avoids feature-history operations so the direct CSG
compiler can be qualified independently.

## Expected behaviour

Forge should preserve the user's constructive intent:

1. create the sphere;
2. join the translated box;
3. cut one centered cylinder along X;
4. cut one centered cylinder along Y;
5. cut one centered cylinder along Z;
6. intersect the result with the clipping box.

The final geometry is created by SolidCraft, not by a Forge geometry kernel.

## Forge API

```python
body = Sphere(20)
body = body + Box(30, 30, 20).move(x=18, z=10)

cross_bore = Cylinder(d=8, h=60).orient(X, Y, Z)
body = body - cross_bore

clip = Box(50, 50, 30).move(z=15)
result = body & clip
```

## Semantics

### Boolean operators

- `a + b` — union/join
- `a - b` — difference/cut
- `a & b` — intersection

### `move(x, y, z)`

For this CSG case, `move()` is an explicit translation of the primitive/tree.
It is not an associative assembly attachment.

### `Cylinder.orient(X, Y, Z)`

`orient()` on a Cylinder asks Forge to use the same cylinder as a cutter
along each requested principal axis. This is different from occurrence
rotation in an assembly.

## Forge model

The result is a `Shape` CSG tree. Because the root starts from `Sphere`,
Forge selects its direct CSG lowering rather than the feature-history Box path.

## SolidCraft mapping

The command contract is:

```text
solid.sphere      operation=new
solid.box         operation=join
solid.cylinder    operation=cut axis=X
solid.cylinder    operation=cut axis=Y
solid.cylinder    operation=cut axis=Z
solid.box         operation=intersect
```

The 60 mm cutters are centered around the origin, therefore their bases are
-30 mm along their respective axes.

## Acceptance criteria

### Q2 — command contract

The generated commands must have the exact operation order above, including:

- translated joined box center = `[18, 0, 10]`;
- cylinder axes = X, Y, Z;
- each cylinder diameter = 8 mm and height = 60 mm;
- clipping box center = `[0, 0, 15]`.

### Q3/Q4 — native SolidCraft

SolidCraft 0.30.1 must:

- accept every generated command;
- produce a valid final body;
- evaluate the complete native timeline without errors.

### Q6 — visual evidence

A native snapshot is retained so the three bores and clipping operation can be
reviewed visually.

## Parametric change

There is no Q5 mutation in this case. Its purpose is primitive CSG lowering,
not saved-design parameter associativity.

## Verification evidence

Fixture: `examples/primitive-csg/scpf/model.py`

Command regression: `scpf/tests/test_qualification_cases.py`

The explicit native qualification run retains command JSON, results,
measurements, saved `.sc`, STEP and PNG evidence.

## Reference models

**OpenSCAD:** this is the closest comparison to ordinary
`union()` / `difference()` / `intersection()` with
`translate()` and rotated cylinders.

**PythonSCAD:** useful as a comparison for Python object/operator ergonomics.
Forge differs by compiling the operation tree to native SolidCraft commands
rather than evaluating geometry itself.
