use std::math::*;
use std::geo3d::*;

part CsgCube(size: Length) {
    body = Sphere(size / 1.5) & Cube(size);
    holes = Cylinder(size, diameter = size / 1.5).orient([X,Y,Z]);
    body - holes;
}

CsgCube(50mm);
