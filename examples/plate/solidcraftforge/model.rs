use solidcraftforge::cad::{DesignError, Edges, Faces, Hole, Length, LengthParam, Part};
use solidcraftforge::csg::LengthUnits;

pub struct Plate;

impl Plate {
    pub fn new(length: Length, width: Length, thickness: Length) -> Result<Part, DesignError> {
        let holes = [
            Hole::with_units((-35).mm(), (-15).mm(), 8.mm())?,
            Hole::with_units( 35.mm(), (-15).mm(), 8.mm())?,
            Hole::with_units( 35.mm(),  15.mm(), 8.mm())?,
            Hole::with_units((-35).mm(),  15.mm(), 8.mm())?,
        ];

        Part::box3d(
            LengthParam::new("length", length)?,
            LengthParam::new("width", width)?,
            LengthParam::new("thickness", thickness)?,
        )?
            .named("Plate")
            .edges(Edges::OuterVertical)
            .fillet(2.mm())?
            .faces(Faces::Top)
            .workplane()
            .circles(&holes)?
            .cut_through()
    }
}

Plate::new(100.mm(), 60.mm(), 10.mm())?
