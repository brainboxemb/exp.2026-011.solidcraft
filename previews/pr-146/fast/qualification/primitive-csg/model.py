"""Core CSG qualification: primitives, transforms and Boolean operations."""


class PrimitiveCsg:
    def build(self):
        body = Sphere(20)
        body = body + Box(30, 30, 20).move(x=18, z=10)

        # Native principal-axis Cylinder; the base point is explicit.
        bore = Cylinder(d=8, h=60, axis=Axis.X).at(-30, 0, 0)
        body = body - bore

        clip = Box(50, 50, 30).move(z=15)
        return body & clip


PrimitiveCsg()
