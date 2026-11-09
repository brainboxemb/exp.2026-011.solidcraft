import cadquery as cq

size = 50.0

body = (
    cq.Workplane("XY").sphere(size / 1.5 / 2.0)
    & cq.Workplane("XY").box(size, size, size)
)

radius = size / 1.5 / 2.0
half = size / 2.0

holes = (
    cq.Workplane("YZ", origin=(-half, 0, 0)).cylinder(size, radius)
    | cq.Workplane("XZ", origin=(0, -half, 0)).cylinder(size, radius)
    | cq.Workplane("XY", origin=(0, 0, -half)).cylinder(size, radius)
)

result = body - holes
