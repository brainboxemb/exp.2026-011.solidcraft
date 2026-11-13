# Primitive CSG

## Use scenario

A Forge user wants to combine a few basic solids directly: join a translated
box to a sphere, drill one cylindrical bore and clip the result with an
intersection box.

## Forge API

```python
body = Sphere(20)
body = body + Box(30, 30, 20).move(x=18, z=10)
body = body - Cylinder(d=8, h=60).move(z=-30)
result = body & Box(50, 50, 30).move(z=15)
```

## Semantics

`+`, `-` and `&` express join, cut and intersection. `move()` is an
explicit shape translation.

`Cylinder()` deliberately has one simple primitive convention: Z is its
axis. Forge no longer provides a Cylinder-specific multi-axis `orient()`
shortcut. If richer primitive orientation is needed, it should be designed as
one general transform/direction concept shared by shapes.

## SolidCraft mapping

```text
solid.sphere      operation=new
solid.box         operation=join
solid.cylinder    operation=cut axis=Z
solid.box         operation=intersect
```

## Acceptance criteria

The command contract fixes the translated box center, the Z-axis bore at
`[0,0,-30]` and the clipping box center. SolidCraft must then accept the
commands, evaluate without timeline errors and produce a reviewable snapshot.

## Parametric change

No Q5 mutation: this case qualifies primitive CSG lowering, not saved-design
associativity.

## Reference models

**OpenSCAD:** the baseline is ordinary `union()`, `difference()`,
`intersection()` and `translate()`.

**PythonSCAD:** the primary reference for pleasant Python object/operator
ergonomics around first-class solids. Forge differs by lowering to native
SolidCraft commands instead of owning the geometry kernel.
