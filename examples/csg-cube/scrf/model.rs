pub struct CsgCube;

#[cad]
impl CsgCube {
    pub fn new(#[parameter] size: f64) -> Shape {
        let body = Sphere::new(size / 1.5) & Cube::new(size);
        let holes = Cylinder::new(size, size / 1.5).orient([X, Y, Z]);

        body - holes
    }
}

CsgCube::new(50.0)
