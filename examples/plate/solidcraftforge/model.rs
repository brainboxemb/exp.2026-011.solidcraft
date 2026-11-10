pub struct Plate;

#[cad]
impl Plate {
    pub fn new(
        #[parameter] length: f64,
        #[parameter] width: f64,
        #[parameter] thickness: f64,
    ) -> Shape {
        let cylinders = Cylinder::new(thickness, 8.0)
            .rectangular_pattern(70.0, 30.0);

        Shape::box3d(length, width, thickness)
            .named("Plate")
            .fillet(Edges::OuterVertical, 2.0)
            .subtract(cylinders)
    }
}

Plate::new(100.0, 60.0, 10.0)
