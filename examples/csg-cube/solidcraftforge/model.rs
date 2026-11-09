use solidcraftforge::cad::Length;
use solidcraftforge::csg::{Cube, Cylinder, ParamLength, Shape, Sphere, X, Y, Z};

pub struct CsgCube {
    shape: Shape,
}

impl CsgCube {
    pub fn new(size: Length) -> Self {
        let size = ParamLength::new("size", size);

        let body = Sphere::new(size / 1.5) & Cube::new(size);
        let holes = Cylinder::new(size, size / 1.5).orient([X, Y, Z]);

        Self {
            shape: body - holes,
        }
    }

    pub fn shape(&self) -> &Shape {
        &self.shape
    }
}
