import cadquery as cq

size = 50.0

body = (
    cq.Workplane("XY").sphere(size / 1.5)
    .intersect(cq.Workplane("XY").box(size, size, size))
)

radius = size / 1.5 / 2.0
hole_x = cq.Workplane("XY").cylinder(size, radius, direct=(1, 0, 0))
hole_y = cq.Workplane("XY").cylinder(size, radius, direct=(0, 1, 0))
hole_z = cq.Workplane("XY").cylinder(size, radius, direct=(0, 0, 1))

holes = hole_x.union(hole_y).union(hole_z)
result = body.cut(holes)
