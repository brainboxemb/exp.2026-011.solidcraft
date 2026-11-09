use std::geo2d::*;
use std::ops::*;

part Plate(length: Length, width: Length, thickness: Length) {
    // µcad 0.6.0 has no native 3D fillet feature. A rounded 2D footprint
    // extruded through the thickness is geometrically equivalent here.
    body = RoundedRect(width = length, height = width, radius = 2mm)
        .extrude(thickness);

    holes = (
        Circle(d = 8mm).translate(x = -35mm, y = -15mm)
        | Circle(d = 8mm).translate(x = 35mm, y = -15mm)
        | Circle(d = 8mm).translate(x = 35mm, y = 15mm)
        | Circle(d = 8mm).translate(x = -35mm, y = 15mm)
    ).extrude(thickness);

    body - holes;
}

Plate(100mm, 60mm, 10mm);
