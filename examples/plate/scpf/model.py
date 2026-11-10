def Plate(length=100.0, width=60.0, thickness=10.0):
    body = Box(length, width, thickness).fillet(2.0, edges="vertical")
    holes = Cylinder(thickness, 8.0).pattern(x=70.0, y=30.0)
    return body - holes

Plate()
