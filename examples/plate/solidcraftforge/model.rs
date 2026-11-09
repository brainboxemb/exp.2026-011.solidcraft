use solidcraftforge::cad::{mm, DesignError, Edges, Faces, Length, Part};

pub struct Plate;

impl Plate {
    pub fn new(length: Length, width: Length, thickness: Length) -> Result<Part, DesignError> {
        Part::box3d(length, width, thickness)?
            .named("Plate")
            .edges(Edges::OuterVertical)
            .fillet(mm(2))?
            .faces(Faces::Top)
            .workplane()
            .rectangular_pattern(mm(70), mm(30))?
            .holes(mm(8))?
            .cut_through()
    }
}

Plate::new(mm(100), mm(60), mm(10))?
