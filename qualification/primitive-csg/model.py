"""Core CSG qualification: primitives, transforms and Boolean operations."""


class PrimitiveCsg:
    def build(self):
        # Rooting the model in Sphere deliberately selects the direct CSG
        # compiler rather than the feature-history Box compiler.
        body = Sphere(20)

        # Translation stays an explicit primitive placement.
        body = body + Box(30, 30, 20).move(x=18, z=10)

        # One semantic cylinder creates three centered native cutters.
        cross_bore = Cylinder(d=8, h=60).orient(X, Y, Z)
        body = body - cross_bore

        # Keep intersection in the same small qualification fixture.
        clip = Box(50, 50, 30).move(z=15)
        return body & clip


PrimitiveCsg()
