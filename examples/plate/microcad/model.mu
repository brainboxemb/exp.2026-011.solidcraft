use std::geo2d::*;
use std::ops::*;

part Plate(length: Length, width: Length, thickness: Length) {
    // µcad 0.6.0 has no native 3D fillet feature. Build the equivalent
    // R2 rounded footprint explicitly, then extrude it.
    r = 2mm;
    corner_x = length / 2 - r;
    corner_y = width / 2 - r;

    rounded_footprint =
        Rect(width = length - 2 * r, height = width)
        | Rect(width = length, height = width - 2 * r)
        | Circle(r = r).translate(x = -corner_x, y = -corner_y)
        | Circle(r = r).translate(x =  corner_x, y = -corner_y)
        | Circle(r = r).translate(x =  corner_x, y =  corner_y)
        | Circle(r = r).translate(x = -corner_x, y =  corner_y);

    body = rounded_footprint.extrude(thickness);

    holes = (
        Circle(d = 8mm).translate(x = -35mm, y = -15mm)
        | Circle(d = 8mm).translate(x = 35mm, y = -15mm)
        | Circle(d = 8mm).translate(x = 35mm, y = 15mm)
        | Circle(d = 8mm).translate(x = -35mm, y = 15mm)
    ).extrude(thickness);

    body - holes;
}

Plate(100mm, 60mm, 10mm);
