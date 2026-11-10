from pythonscad import *


def Plate(length=100.0, width=60.0, thickness=10.0):
    body = cube([length, width, thickness], center=True)

    # Select only the four vertical corner edges. The mask stops before the
    # top and bottom faces, so their horizontal edges are not selected.
    mask_height = thickness - 4.0
    mask = (
        (cube([6, 6, mask_height], center=True) + [-length / 2, -width / 2, 0])
        | (cube([6, 6, mask_height], center=True) + [ length / 2, -width / 2, 0])
        | (cube([6, 6, mask_height], center=True) + [ length / 2,  width / 2, 0])
        | (cube([6, 6, mask_height], center=True) + [-length / 2,  width / 2, 0])
    )
    body = body.fillet(2.0, mask, fn=16)

    holes = (
        (cylinder(h=thickness + 2, d=8, center=True) + [-35, -15, 0])
        | (cylinder(h=thickness + 2, d=8, center=True) + [ 35, -15, 0])
        | (cylinder(h=thickness + 2, d=8, center=True) + [ 35,  15, 0])
        | (cylinder(h=thickness + 2, d=8, center=True) + [-35,  15, 0])
    )

    return (body - holes).up(thickness / 2)


result = Plate()
result.show()
