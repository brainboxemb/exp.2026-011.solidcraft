use solidcraftforge::cad::{DesignError, Edges, Part};
use solidcraftforge::csg::Cylinder;

pub struct Plate;

impl Plate {
    pub fn new(length: f64, width: f64, thickness: f64) -> Result<Part, DesignError> {
        let cylinders = Cylinder::new(thickness, 8.0)
            .rectangular_pattern(70.0, 30.0)?;

        Part::box3d(length, width, thickness)?
            .named("Plate")
            .edges(Edges::OuterVertical)
            .fillet(2.0)?
            .subtract(cylinders)
    }
}

Plate::new(100.0, 60.0, 10.0)?
