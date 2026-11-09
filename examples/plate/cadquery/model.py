import cadquery as cq


def Plate(length=100.0, width=60.0, thickness=10.0):
    body = cq.Workplane("XY").box(
        length, width, thickness, centered=(True, True, False)
    )
    body = body.edges("|Z").fillet(2.0)

    holes = [
        (-35.0, -15.0),
        (35.0, -15.0),
        (35.0, 15.0),
        (-35.0, 15.0),
    ]
    return body.faces(">Z").workplane().pushPoints(holes).hole(8.0)


result = Plate()
