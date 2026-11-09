from pythonscad import *


def CsgCube(size):
    body = sphere(r=size / 1.5) & cube(size, center=True)

    holes = (
        cylinder(h=size, d=size / 1.5, center=True).roty(90)
        | cylinder(h=size, d=size / 1.5, center=True).rotx(90)
        | cylinder(h=size, d=size / 1.5, center=True)
    )

    return body - holes


result = CsgCube(50)
result.show()
