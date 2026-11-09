use solidcraftforge::cad::Length;
use solidcraftforge::csg::{Cube, Cylinder, LengthUnits, ParamLength, Shape, Sphere, X, Y, Z};

pub struct CsgCube;

impl CsgCube {
    pub fn new(size: Length) -> Shape {
        let size = ParamLength::new("size", size);

        let body = Sphere::new(size / 1.5) & Cube::new(size);
        let holes = Cylinder::new(size, size / 1.5).orient([X, Y, Z]);

        body - holes
    }
}

CsgCube::new(50.mm())
