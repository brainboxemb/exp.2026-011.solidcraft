"""Core CSG qualification: primitives, transforms and Boolean operations."""


class PrimitiveCsg:
    def build(self):
        body = Sphere(20)
        body = body + Box(30, 30, 20).move(x=18, z=10)

        # Cylinder stays deliberately simple: its primitive axis is Z.
        bore = Cylinder(d=8, h=60).move(z=-30)
        body = body - bore

        clip = Box(50, 50, 30).move(z=15)
        return body & clip


PrimitiveCsg()
