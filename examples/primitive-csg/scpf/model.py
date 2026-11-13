"""Core CSG qualification: primitives, transforms and boolean operations."""


class PrimitiveCsg:
    def build(self):
        # Start with Sphere so the compiler deliberately uses the CSG path
        # instead of the feature-history Box path.
        body = Sphere(20)

        # Translation of a primitive stays a native CSG placement.
        body = body + Box(30, 30, 20).move(x=18, z=10)

        # One semantic cylinder creates three centered native cutters.  This
        # qualifies the X/Y/Z shorthand tokens and Cylinder.orient() together.
        cross_bore = Cylinder(d=8, h=60).orient(X, Y, Z)
        body = body - cross_bore

        # Keep an intersection operation in the same tiny fixture.
        clip = Box(50, 50, 30).move(z=15)
        return body & clip


PrimitiveCsg()
