def CsgCube(size=50.0):
    body = Sphere(size / 1.5) & Cube(size)
    holes = Cylinder(size, size / 1.5).orient(X, Y, Z)
    return body - holes

CsgCube()
