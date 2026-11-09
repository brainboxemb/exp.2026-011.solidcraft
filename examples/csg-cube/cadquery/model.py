import cadquery as cq

size = 50.0

body = (
    cq.Workplane("XY").sphere(size / 1.5)
    & cq.Workplane("XY").box(size, size, size)
)

radius = size / 1.5 / 2.0
holes = (
    cq.Workplane("XY").cylinder(size, radius, direct=(1, 0, 0))
    | cq.Workplane("XY").cylinder(size, radius, direct=(0, 1, 0))
    | cq.Workplane("XY").cylinder(size, radius, direct=(0, 0, 1))
)

result = body - holes
