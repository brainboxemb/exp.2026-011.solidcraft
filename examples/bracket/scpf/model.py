def Bracket(width=60.0, thickness=6.0):
    # L-shaped profile in XZ; positive thickness, negative Y extrusion.
    profile = Polygon(
        [(0, 0), (40, 0), (40, thickness),
         (thickness, thickness), (thickness, 30), (0, 30)],
        plane="XZ",
    )
    body = profile.extrude(width, direction="negative")
    body = body.fillet(2, edges=[(40, -width / 2, thickness)])

    # The XY workplane is at z=0. Cut towards positive Z to intersect
    # the 0..thickness base plate; the uploaded reference cut was negative.
    return body.holes([(25, -15), (25, -45)],
                      diameter=8, depth=thickness, direction="positive")

Bracket()
