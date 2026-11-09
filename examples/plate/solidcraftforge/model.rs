pub struct Plate;

impl Plate {
    pub fn new(length: f64, width: f64, thickness: f64) -> Shape {
        let cylinders = Cylinder::new(thickness, 8.0)
            .rectangular_pattern(70.0, 30.0);

        Shape::box3d(length, width, thickness)
            .named("Plate")
            .fillet(Edges::OuterVertical, 2.0)
            .subtract(cylinders)
    }
}

Plate::new(100.0, 60.0, 10.0)
