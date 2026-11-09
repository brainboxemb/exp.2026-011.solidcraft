use solidcraftforge::cad::{DesignError, Edges, Faces, Hole, Length, LengthParam, Part};
use solidcraftforge::csg::LengthUnits;

pub struct Plate {
    part: Part,
}

impl Plate {
    pub fn new(length: Length, width: Length, thickness: Length) -> Result<Self, DesignError> {
        let holes = [
            Hole::with_units((-35).mm(), (-15).mm(), 8.mm())?,
            Hole::with_units( 35.mm(), (-15).mm(), 8.mm())?,
            Hole::with_units( 35.mm(),  15.mm(), 8.mm())?,
            Hole::with_units((-35).mm(),  15.mm(), 8.mm())?,
        ];

        let part = Part::box3d(
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
            .cut_through()?;

        Ok(Self { part })
    }

    pub fn part(&self) -> &Part {
        &self.part
    }
}
